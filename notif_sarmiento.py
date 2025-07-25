import requests
from bs4 import BeautifulSoup

# Lista de instancias de Nitter
NITTER_INSTANCIAS = [
    "https://nitter.poast.org",
    "https://nitter.privacyredirect.com",
    "https://lightbrd.com",
    "https://nitter.space",
    "https://nitter.tiekoetter.com",
    "https://nitter.kareem.one",
    "https://nuku.trabun.org",
    "https://xcancel.com"
]


CUENTA = "/InfoTSarmiento"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def obtener_tweet_valido():
    for base_url in NITTER_INSTANCIAS:
        url = base_url + CUENTA
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                print(f"✅ Usando instancia: {base_url}")
                return response.text, base_url
            else:
                print(f"⚠️ {base_url} respondió con status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accediendo a {base_url}: {e}")
    raise Exception("🚫 No se pudo acceder a ninguna instancia de Nitter.")

# Uso
html, instancia_utilizada = obtener_tweet_valido()
soup = BeautifulSoup(html, "lxml")

# A partir de acá, parseás como antes
tweet_div = soup.find("div", class_="timeline-item")
print(html[:1000])  # Imprime primeros 1000 caracteres del HTML
if tweet_div is None:
    print("❌ No se encontró ningún tweet en la página.")
    exit(1)

tweet_text = tweet_div.find("div", class_="tweet-content").text.strip()
tweet_link = tweet_div.find("a", class_="tweet-link")["href"]
tweet_url = instancia_utilizada + tweet_link
tweet_id = tweet_link

# Mostrar resultados
print("📝 Último tweet:", tweet_text)
print("🔗 Link:", tweet_url)
print("🆔 ID:", tweet_id)
