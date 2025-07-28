from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import requests

# Cargar .env
load_dotenv()
TW_USER = os.getenv("TWITTER_USER")
TW_PASS = os.getenv("TWITTER_PASS")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Enviar mensaje por Telegram
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": mensaje
    }
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print("✅ Enviado a Telegram")
    else:
        print("❌ Error enviando a Telegram:", r.text)

# Configurar navegador
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
# options.add_argument('--headless')  # Descomentá si no querés ver el navegador

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Login a Twitter
    driver.get("https://twitter.com/login")
    time.sleep(5)

    driver.find_element(By.NAME, "text").send_keys(TW_USER + Keys.RETURN)
    time.sleep(3)

    # A veces pide dos veces el user
    try:
        driver.find_element(By.NAME, "text").send_keys(TW_USER + Keys.RETURN)
        time.sleep(3)
    except:
        pass

    driver.find_element(By.NAME, "password").send_keys(TW_PASS + Keys.RETURN)
    time.sleep(5)

    # Ir al perfil de @InfoTSarmiento
    driver.get("https://twitter.com/InfoTSarmiento")
    time.sleep(5)

    # Extraer el primer tweet
    tweet = driver.find_element(By.XPATH, '(//article)[1]')
    contenido = tweet.text.strip()
    print("🆕 Último tweet:")
    print(contenido)

    # Enviar por Telegram
    enviar_telegram(contenido)

finally:
    driver.quit()
