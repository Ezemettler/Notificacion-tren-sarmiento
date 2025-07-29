# Notificación Tren Sarmiento

## ¿Qué es este proyecto?

Este proyecto automatiza la consulta de los últimos tweets de la cuenta oficial de Twitter del Tren Sarmiento (@InfoTSarmiento) y envía notificaciones a un bot de Telegram. Así, recibo en tiempo real actualizaciones sobre el estado del servicio sin necesidad de ingresar manualmente a Twitter.

El script utiliza Selenium para abrir un navegador Chrome en modo headless, hacer login en Twitter con credenciales seguras y extraer el último tweet publicado. Luego, envía el contenido directamente a Telegram.


## ¿Por qué hice este proyecto? ¿Qué problema resuelve?

Uso el Tren Sarmiento diariamente y para evitar tener que acordarme y entrar a chequear el estado del tren en la cuenta, me cansaba de tener que entrar a Twitter para revisar si había novedades o problemas en el servicio. Especialmente antes de ir y al salir del trabajo, necesitaba saber si el tren circulaba con normalidad o si había interrupciones para planificar mejor mis viajes.

Con este proyecto, recibo automáticamente los avisos más recientes en Telegram en horarios clave (mañana y tarde, días hábiles), sin tener que revisar Twitter manualmente. Esto me ahorra tiempo y estrés, ayudándome a evitar llegar a la estación sin información y a buscar alternativas si es necesario.


## ¿Cómo funciona?

- El script corre con Python y Selenium, abre un navegador Chrome de forma invisible (headless), y hace login con usuario y contraseña de Twitter guardados en variables de entorno.
- Navega al perfil oficial del Tren Sarmiento y extrae el tweet más reciente.
- Envía ese tweet como mensaje a un bot de Telegram usando la API oficial.
- Está programado para ejecutarse automáticamente en horarios definidos mediante GitHub Actions, por lo que no necesita que la computadora esté encendida.

## Stack y tecnologías utilizadas

- **Python**: lenguaje principal del script.
- **Selenium** con **webdriver-manager**: para automatizar la interacción con el navegador Chrome.
- **python-dotenv**: para cargar credenciales y tokens desde un archivo `.env` o variables de entorno.
- **requests**: para enviar mensajes a Telegram a través de su API.
- **GitHub Actions**: para programar la ejecución automática del script en la nube.
- **Telegram Bot API**: para recibir notificaciones directas en un chat o grupo de Telegram.


**Autor:** Ezequiel Mettler  
**Fecha:** Julio 2025
