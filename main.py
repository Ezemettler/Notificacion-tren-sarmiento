from utils import obtener_tweet_mas_reciente, enviar_a_telegram
from dotenv import load_dotenv


load_dotenv()


def main():
    """Función principal optimizada para obtener solo el tweet más reciente"""
    print("🔄 Buscando el tweet más reciente del Sarmiento...")
    
    # Obtener solo el tweet más reciente
    resultado = obtener_tweet_mas_reciente(
        usuario="InfoTSarmiento",
        hashtag="EstadoDelServicio",
        dias_atras=7
    )
    
    if resultado:
        texto, fecha = resultado
        print("✅ TWEET MÁS RECIENTE ENCONTRADO:")
        print(f"📅 Fecha: {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Contenido: {texto}")
        
        # Opcionalmente enviar a Telegram
        if enviar_a_telegram(texto):
            print("✅ Enviado a Telegram")
        else:
            print("⚠️ No se pudo enviar a Telegram")
            
        return texto, fecha
    else:
        print("❌ No se encontraron tweets recientes que cumplan los criterios")
        return None, None

if __name__ == "__main__":
    main()