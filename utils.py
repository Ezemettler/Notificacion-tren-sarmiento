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
        # Nitter usa formatos como "Aug 26, 2025 · 2:30 PM UTC"
        # También puede ser "2h" o "Aug 26" etc.
        
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
            # Formato: "Aug 26, 2025 · 2:30 PM UTC"
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
        
        # Si no se puede parsear, usar fecha actual
        print(f"⚠️ No se pudo parsear la fecha: {fecha_texto}")
        return datetime.now(timezone.utc)
        
    except Exception as e:
        print(f"⚠️ Error parseando fecha '{fecha_texto}': {e}")
        return datetime.now(timezone.utc)

def obtener_tweets_nitter(usuario="InfoTSarmiento", max_tweets=50):
    """Obtiene tweets desde Nitter"""
    driver = iniciar_driver()
    
    try:
        # URL del perfil en Nitter
        url = f"https://nitter.net/{usuario}"
        print(f"🌐 Accediendo a {url}")
        driver.get(url)
        
        # Esperar a que cargue
        time.sleep(5)
        
        # Verificar si la página cargó correctamente
        if "Nitter" not in driver.title:
            print("⚠️ Posible problema cargando Nitter")
        
        tweet_data = []
        tweets_procesados = set()
        scrolls_sin_nuevos = 0
        max_scrolls_sin_nuevos = 3
        
        while len(tweet_data) < max_tweets and scrolls_sin_nuevos < max_scrolls_sin_nuevos:
            # Buscar tweets con los selectores de Nitter
            tweet_selectors = [
                '.timeline-item',
                '.tweet-content',
                'div[class*="timeline"]'
            ]
            
            tweets_encontrados = []
            for selector in tweet_selectors:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                if elementos:
                    tweets_encontrados = elementos
                    print(f"✅ Encontrados {len(elementos)} elementos con selector: {selector}")
                    break
            
            if not tweets_encontrados:
                print("❌ No se encontraron tweets en Nitter")
                break
            
            tweets_antes = len(tweet_data)
            
            for elemento in tweets_encontrados:
                try:
                    # Verificar si es realmente un tweet
                    if not elemento.text.strip():
                        continue
                    
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
                        # Si no encuentra selector específico, usar el texto completo
                        texto = elemento.text.strip()
                    else:
                        texto = texto_elemento.text.strip()
                    
                    if not texto or len(texto) < 10:
                        continue
                    
                    # Crear ID único para evitar duplicados
                    tweet_id = hash(texto[:100])
                    if tweet_id in tweets_procesados:
                        continue
                    tweets_procesados.add(tweet_id)
                    
                    # Buscar la fecha
                    fecha_selectors = [
                        '.tweet-date a',
                        '.tweet-published',
                        'a[title*="20"]',
                        'span[class*="date"]'
                    ]
                    
                    fecha = None
                    fecha_texto = ""
                    
                    for fecha_sel in fecha_selectors:
                        try:
                            fecha_elemento = elemento.find_element(By.CSS_SELECTOR, fecha_sel)
                            if fecha_elemento:
                                # Probar diferentes atributos
                                fecha_texto = (fecha_elemento.get_attribute('title') or 
                                             fecha_elemento.get_attribute('datetime') or 
                                             fecha_elemento.text.strip())
                                if fecha_texto:
                                    break
                        except:
                            continue
                    
                    if fecha_texto:
                        fecha = convertir_fecha_nitter(fecha_texto)
                    else:
                        # Si no encontramos fecha, usar orden en la página (más recientes primero)
                        fecha = datetime.now(timezone.utc)
                        print(f"⚠️ No se encontró fecha para tweet, usando fecha actual")
                    
                    tweet_data.append((texto, fecha))
                    print(f"✅ Tweet {len(tweet_data)}: {fecha.strftime('%Y-%m-%d %H:%M')} - {texto[:80]}...")
                    
                    if len(tweet_data) >= max_tweets:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error procesando elemento: {e}")
                    continue
            
            # Verificar si se agregaron tweets nuevos
            if len(tweet_data) == tweets_antes:
                scrolls_sin_nuevos += 1
                print(f"📜 Scroll sin nuevos tweets ({scrolls_sin_nuevos}/{max_scrolls_sin_nuevos})")
            else:
                scrolls_sin_nuevos = 0
                print(f"📜 Scroll exitoso: {len(tweet_data) - tweets_antes} tweets nuevos")
            
            # Hacer scroll para cargar más
            if len(tweet_data) < max_tweets:
                driver.execute_script("window.scrollBy(0, 2000);")
                time.sleep(3)
        
        print(f"✅ Total de tweets obtenidos: {len(tweet_data)}")
        
        # Ordenar por fecha descendente (más reciente primero)
        tweet_data.sort(key=lambda x: x[1], reverse=True)
        
        return tweet_data
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return []
    finally:
        driver.quit()



def filtrar_tweets(tweets, hashtag=None, dias_atras=7):
    """Filtra tweets por hashtag y días recientes"""
    from datetime import timedelta
    
    tweets_filtrados = []
    fecha_limite = datetime.now(timezone.utc) - timedelta(days=dias_atras)
    
    print(f"🔍 Filtrando tweets desde: {fecha_limite.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Fecha actual: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    
    for i, (texto, fecha) in enumerate(tweets):
        dias_diferencia = (datetime.now(timezone.utc) - fecha).days
        print(f"📅 Tweet {i+1}: {fecha.strftime('%Y-%m-%d %H:%M:%S')} - Hace {dias_diferencia} días")
        
        # Filtrar por fecha reciente
        if fecha < fecha_limite:
            print(f"   ⏰ Descartado por antigüedad (>{dias_atras} días)")
            continue
            
        # Filtrar por hashtag (más flexible)
        if hashtag:
            # Normalizar hashtag
            hashtag_clean = hashtag.replace('#', '').lower()
            texto_lower = texto.lower()
            
            # Buscar hashtag con diferentes variaciones
            encontrado = False
            variaciones = [
                hashtag.lower(),
                hashtag_clean,
                f"#{hashtag_clean}",
                hashtag_clean.replace('del', 'del'),
                hashtag_clean.replace('estado', 'estado'),
                'estadodelservicio',
                '#estadodelservicio'
            ]
            
            for variacion in variaciones:
                if variacion in texto_lower:
                    print(f"   ✅ Coincide con: '{variacion}'")
                    encontrado = True
                    break
            
            if encontrado:
                tweets_filtrados.append((texto, fecha))
            else:
                print(f"   ❌ No coincide con hashtag: {hashtag}")
                print(f"       Texto: {texto[:100]}...")
        else:
            tweets_filtrados.append((texto, fecha))
    
    return tweets_filtrados



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
