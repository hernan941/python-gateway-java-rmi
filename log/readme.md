# Sistema de Log Centralizado con RMI

Este sistema permite a los clientes enviar mensajes de log a un servidor centralizado a través de RMI.

## Requisitos

- Java JDK 8 o superior. (Probado con java 11 y powershell)

## Instrucciones

1. Compilar los archivos `.java`.
    javac -cp lib/py4j0.10.9.7.jar LogInterface.java LogServer.java LogClient.java LogClientGateway.java

2. Iniciar el RMI Registry.
    start rmiregistry

3. Ejecutar el servidor.
    java LogServer

4. Ejecutar el cliente - Puente.
- En un equipo diferente, reemplace `host` con la dirección IP del servidor:
  ```
  java -cp ".;lib/py4j0.10.9.7.jar" LogClientGateway
  ```

El servidor escuchará los mensajes de log enviados por los clientes y los escribirá en un archivo llamado `log.txt`.