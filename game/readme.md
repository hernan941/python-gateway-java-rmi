## Ejercicio 2.
El ejercicio 2 simula un juego de tablero lineal, sin eventos, en el cual dos o mas equipos avanzan mediante la suma de el lanzamiento de los dados de todos los miembros del equipo.
Para el desarrollo se utilizó:
- Python 3.10

Ademas de instalar la libreria en requirements.txt

y las librerías importadas en el inicio del código:
- socket: para la gestión de conexiones de red
- threading: para manejar la concurrencia
- time: para esperar a ciertas acciones
- random: para generar números aleatorios

Para ejecutar el proyecto, se debe correr el archivo server.py y luego el al menos dos instancias de client.py en su consola de preferencia. El servidor no recibe comandos de entrada. El cliente si recibe comandos de entrada.
Al iniciar el cliente, este se conecta automáticamente al servidor y se le asigna un ID de jugador. Este ID se utiliza también para crear el puerto por el que se comunicará con sus compañeros de equipo.

Los comandos (funcionales) para empezar el juego desde cliente, son:
- unirse X: Envía un mensaje al servidor y le permite al jugador unirse al equipo X, siempre y cuando este esté creado. X es un numero entero. Si es el primer jugador que entra al equipo, se le designa como líder. No existe cantidad máxima de jugadores por equipo.
- crear: Envía un mensaje al servidor y le permite al jugador crear un equipo. El ID del equipo se genera en el servidor y se le entrega al jugador. Al crear el equipo, se une automáticamente y se le designa como líder. No existe limite máximo de equipos.
- equipo: Envía un mensaje al servidor solicitando la información actualizada de los miembros del equipo (IP y puertos). Pueden enviarlo jugadores normales como lideres de equipo.
- iniciar: Envía un mensaje a sus compañeros de equipo para informar que está listo para iniciar la partida. Pueden enviarlo jugadores normales y lideres de equipo.
- iniciar partida: Envía un mensaje al servidor, siempre y cuando todos los jugadores del equipo hayan confirmado que están listos para empezar a jugar con el comando "iniciar". Este mensaje solo puede enviarlo el líder de equipo.
- dado: Genera un numero aleatorio entero entre el rango de números definido al inicio del código (actual entre 1 y 6). Este resultado se envía automáticamente a todos los compañeros de equipo para que lo registren.
- enviar jugada: Verifica haber recibido todos los resultados de los dados del equipo y envía la suma como jugada grupal al servidor. Luego de enviar el mensaje, indica a los miembros del equipo borrar sus datos de juego del turno anterior. 
- hacer lider: hace lider si es que no hay ningun miembro conectado

Las variables modificables (no de entorno) corresponden al mínimo y máximo del dado y al largo del tablero, siendo los primeros dos, variables del cliente y el tercero, variable del servidor. 

El servidor define el orden de juego de los equipos al azar y controla la lógica general del juego. 
El juego no permite que los miembros del grupo acepten a un nuevo integrante. Este siempre es aceptado.
Las decisiones que toma el equipo y comunica al servidor mediante el líder son el resultado de los dados y cuando están listos para iniciar el juego.

El juego termina después de que en una ronda algún equipo haya alcanzado el máximo del tablero. 