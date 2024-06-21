import py4j.GatewayServer;



public class LogClientGateway {
    private LogClient logClient;

    public LogClientGateway() {
        // Configura tu cliente RMI aquí. Asume localhost, puerto 1099, y el nombre del servicio RMI.
        this.logClient = new LogClient("localhost", 5000, "LogServer");
    }

    public void logMessage(String message) {
        logClient.logMessage(message);
    }

    public static void main(String[] args) {
        LogClientGateway gateway = new LogClientGateway();
        GatewayServer server = new GatewayServer(gateway);
        server.start();
        System.out.println("Gateway Server Started");
    }
}