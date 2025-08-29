import os, time, re, requests
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



def iniciar_driver():
    """Configura y devuelve el driver de Chrome en modo headless"""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver



def convertir_fecha_nitter(fecha_texto):
    """Convierte el formato de fecha de Nitter a datetime"""
    try:
        fecha_texto = fecha_texto.strip()
        
        # Si es formato relativo como "2h", "1d", etc.
        if re.match(r'^\d+[smhd]$', fecha_texto):
            from datetime import timedelta
            numero = int(re.findall(r'\d+', fecha_texto)[0])
            unidad = fecha_texto[-1]
            
            ahora = datetime.now(timezone.utc)
            
            if unidad == 's':
                return ahora - timedelta(seconds=numero)
            elif unidad == 'm':
                return ahora - timedelta(minutes=numero)
            elif unidad == 'h':
                return ahora - timedelta(hours=numero)
            elif unidad == 'd':
                return ahora - timedelta(days=numero)
        
        # Si tiene formato completo con hora
        if '·' in fecha_texto and ('AM' in fecha_texto or 'PM' in fecha_texto):
            partes = fecha_texto.split('·')
            fecha_parte = partes[0].strip()
            hora_parte = partes[1].strip().replace(' UTC', '')
            fecha_completa = f"{fecha_parte} {hora_parte}"
            return datetime.strptime(fecha_completa, "%b %d, %Y %I:%M %p").replace(tzinfo=timezone.utc)
        
        # Si solo tiene fecha sin hora
        if re.match(r'^[A-Za-z]{3} \d{1,2}, \d{4}$', fecha_texto):
            return datetime.strptime(fecha_texto, "%b %d, %Y").replace(tzinfo=timezone.utc)
        
        # Si solo tiene mes y día
        if re.match(r'^[A-Za-z]{3} \d{1,2}$', fecha_texto):
            año_actual = datetime.now().year
            fecha_completa = f"{fecha_texto}, {año_actual}"
            return datetime.strptime(fecha_completa, "%b %d, %Y").replace(tzinfo=timezone.utc)
        
        return datetime.now(timezone.utc)
        
    except Exception:
        return datetime.now(timezone.utc)
    


def obtener_tweet_mas_reciente(usuario="InfoTSarmiento", hashtag="EstadoDelServicio", dias_atras=7):
    """Obtiene solo el tweet más reciente que cumpla los criterios"""
    driver = iniciar_driver()
    
    try:
        url = f"https://nitter.net/{usuario}"
        driver.get(url)
        time.sleep(3)  # Tiempo reducido
        
        # Buscar tweets con los selectores de Nitter
        tweet_selectors = ['.timeline-item', '.tweet-content', 'div[class*="timeline"]']
        
        tweets_encontrados = []
        for selector in tweet_selectors:
            elementos = driver.find_elements(By.CSS_SELECTOR, selector)
            if elementos:
                tweets_encontrados = elementos
                break
        
        if not tweets_encontrados:
            return None
        
        # Variables para el filtro
        from datetime import timedelta
        fecha_limite = datetime.now(timezone.utc) - timedelta(days=dias_atras)
        hashtag_clean = hashtag.replace('#', '').lower() if hashtag else None
        
        # Procesar tweets hasta encontrar el más reciente que cumpla criterios
        tweet_mas_reciente = None
        fecha_mas_reciente = None
        
        for elemento in tweets_encontrados:
            try:
                # Buscar el contenido del tweet
                tweet_text_selectors = [
                    '.tweet-content .tweet-body',
                    '.tweet-text',
                    'div[class*="tweet-content"]'
                ]
                
                texto_elemento = None
                for txt_sel in tweet_text_selectors:
                    try:
                        texto_elemento = elemento.find_element(By.CSS_SELECTOR, txt_sel)
                        if texto_elemento:
                            break
                    except:
                        continue
                
                if not texto_elemento:
                    texto = elemento.text.strip()
                else:
                    texto = texto_elemento.text.strip()
                
                if not texto or len(texto) < 10:
                    continue
                
                # Buscar la fecha
                fecha_selectors = [
                    '.tweet-date a',
                    '.tweet-published',
                    'a[title*="20"]',
                    'span[class*="date"]'
                ]
                
                fecha_texto = ""
                for fecha_sel in fecha_selectors:
                    try:
                        fecha_elemento = elemento.find_element(By.CSS_SELECTOR, fecha_sel)
                        if fecha_elemento:
                            fecha_texto = (fecha_elemento.get_attribute('title') or 
                                         fecha_elemento.get_attribute('datetime') or 
                                         fecha_elemento.text.strip())
                            if fecha_texto:
                                break
                    except:
                        continue
                
                fecha = convertir_fecha_nitter(fecha_texto) if fecha_texto else datetime.now(timezone.utc)
                
                # Verificar si cumple criterios de fecha
                if fecha < fecha_limite:
                    continue
                
                # Verificar hashtag si se especifica
                if hashtag_clean:
                    texto_lower = texto.lower()
                    variaciones = [
                        hashtag.lower(),
                        hashtag_clean,
                        f"#{hashtag_clean}",
                        'estadodelservicio',
                        '#estadodelservicio'
                    ]
                    
                    if not any(variacion in texto_lower for variacion in variaciones):
                        # Si no coincide con hashtag, verificar palabras clave relacionadas
                        palabras_clave = ["estado", "servicio", "línea", "demora", "normal", "circula"]
                        if not any(palabra in texto_lower for palabra in palabras_clave):
                            continue
                
                # Si es el primer tweet válido o es más reciente que el anterior
                if fecha_mas_reciente is None or fecha > fecha_mas_reciente:
                    tweet_mas_reciente = texto
                    fecha_mas_reciente = fecha
                
                # Como los tweets suelen estar ordenados cronológicamente, 
                # el primero que cumple criterios suele ser el más reciente
                break
                        
            except Exception:
                continue
        
        return (tweet_mas_reciente, fecha_mas_reciente) if tweet_mas_reciente else None
        
    except Exception:
        return None
    finally:
        driver.quit()



def enviar_a_telegram(texto):
    """Envía un mensaje a Telegram usando variables de entorno"""
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        mensaje = f"✅ Servicio Tren Sarmiento:\n{texto}"
        
        # Endpoint de la API de Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"       
        
        # Parámetros necesarios para enviar el mensaje
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje
        }
        requests.get(url, params=params)    # Enviamos el mensaje con un GET request a la API de Telegram
        print("✅ Enviado a Telegram")
    else:
        print("⚠️ No se encontraron las variables de entorno para Telegram")