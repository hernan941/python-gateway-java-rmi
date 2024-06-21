# Sistema Distribuido de Juego con Registro de Log

Este proyecto consiste en un sistema distribuido para un juego, con un servidor de juego, un cliente de juego y un sistema de registro de logs.

## Estructura del Proyecto

El proyecto se divide en dos partes principales: `game` y `log`.

### Game

La carpeta `game` contiene el cliente y el servidor del juego.

- `client.py`: Cliente del juego que se conecta al servidor para jugar.
- `server.py`: Servidor del juego que gestiona las conexiones de los clientes y la lógica del juego.
- `requirements.txt`: Dependencias necesarias para ejecutar el juego.
- `readme.md`: Instrucciones específicas para la configuración y ejecución del juego.

### Log

La carpeta `log` contiene el sistema de registro de logs, implementado en Java, que permite registrar eventos del sistema.

- `LogServer.java`: Servidor de logs que recibe y procesa los registros.
- `LogClient.java`: Cliente de logs que envía registros al servidor.
- `LogInterface.java`: Interfaz RMI utilizada para la comunicación entre el cliente y el servidor de logs.
- `lib/py4j0.10.9.7.jar`: Biblioteca necesaria para la integración de Python y Java.
- `readme.md`: Instrucciones específicas para la configuración y ejecución del sistema de logs.

## Requisitos

Para ejecutar el proyecto, necesitarás:

- Python 3.x para la parte del juego.
- Java JDK para el sistema de registro de logs.
- Las dependencias de Python especificadas en `game/requirements.txt`.

## Instalación y Ejecución

1. Clona el repositorio en tu máquina local.
2. Instala las dependencias de Python con `pip install -r game/requirements.txt`.
3. Ejecuta el servidor y el cliente del juego siguiendo las instrucciones en `game/readme.md`.
4. Ejecuta el servidor y el cliente de logs siguiendo las instrucciones en `log/readme.md`.