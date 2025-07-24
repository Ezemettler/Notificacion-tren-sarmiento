import os
import requests
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Mensaje de prueba
mensaje = "🚊 ¡Bot funcionando correctamente! Este es un mensaje de prueba."

# Endpoint de Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Parámetros del mensaje
params = {
    "chat_id": CHAT_ID,
    "text": mensaje
}

# Enviar mensaje
resp = requests.get(url, params=params)

# Confirmar respuesta
if resp.status_code == 200:
    print("✅ Mensaje enviado con éxito.")
else:
    print("❌ Error al enviar mensaje:")
    print(resp.text)
