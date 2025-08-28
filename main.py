from utils import obtener_tweets_nitter, filtrar_tweets
from dotenv import load_dotenv


load_dotenv()


def main():
    print("🔄 Iniciando búsqueda de tweets del Sarmiento desde Nitter...")
    
    # Obtener tweets desde Nitter
    tweets = obtener_tweets_nitter(usuario="InfoTSarmiento", max_tweets=30)
    
    if not tweets:
        print("⚠️ No se encontraron tweets")
        return
    
    print(f"\n📊 Se obtuvieron {len(tweets)} tweets en total")
    
    # Mostrar algunos tweets recientes para debug
    print("\n🔍 Últimos 5 tweets (para verificar):")
    for i, (texto, fecha) in enumerate(tweets[:5]):
        print(f"{i+1}. {fecha.strftime('%Y-%m-%d %H:%M:%S')}: {texto[:120]}...")
    
    # Filtrar por hashtag y fechas recientes
    hashtag = "EstadoDelServicio"  # Sin el #
    tweets_filtrados = filtrar_tweets(tweets, hashtag=hashtag, dias_atras=7)
    
    if not tweets_filtrados:
        print(f"⚠️ No se encontraron tweets recientes con #{hashtag}")
        print("💡 Probando búsqueda más amplia...")
        
        # Búsqueda más amplia sin hashtag específico
        tweets_recientes = filtrar_tweets(tweets, dias_atras=7)
        print(f"📋 Tweets recientes encontrados: {len(tweets_recientes)}")
        
        # Buscar manualmente tweets que contengan palabras clave
        palabras_clave = ["estado", "servicio", "línea", "demora", "normal", "circula"]
        tweets_relacionados = []
        
        for texto, fecha in tweets_recientes:
            if any(palabra in texto.lower() for palabra in palabras_clave):
                tweets_relacionados.append((texto, fecha))
        
        if tweets_relacionados:
            print(f"🎯 Tweets relacionados con el servicio: {len(tweets_relacionados)}")
            tweets_filtrados = tweets_relacionados
    
    if tweets_filtrados:
        print(f"\n📢 Tweets filtrados encontrados: {len(tweets_filtrados)}")
        
        for i, (texto, fecha) in enumerate(tweets_filtrados):
            print(f"\n{i+1}. 📅 {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📝 {texto}")
            print(f"   {'='*80}")
        
        # El más reciente ya está primero por el ordenamiento
        tweet_mas_reciente = tweets_filtrados[0]
        print(f"\n✅ TWEET MÁS RECIENTE CON FILTROS:")
        print(f"📅 Fecha: {tweet_mas_reciente[1].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Contenido completo:")
        print(f"{tweet_mas_reciente[0]}")
        
    else:
        print("❌ No se encontraron tweets que cumplan los criterios")
        
        # Mostrar todos los tweets recientes como fallback
        tweets_recientes = filtrar_tweets(tweets, dias_atras=7)
        if tweets_recientes:
            print(f"\n📋 Mostrando todos los tweets recientes ({len(tweets_recientes)}):")
            for i, (texto, fecha) in enumerate(tweets_recientes[:3]):
                print(f"{i+1}. {fecha.strftime('%Y-%m-%d %H:%M:%S')}: {texto[:100]}...")

if __name__ == "__main__":
    main()