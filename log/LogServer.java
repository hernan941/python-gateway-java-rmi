import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.rmi.RemoteException;

public class LogServer implements LogInterface {
    public LogServer() {}

    public void logMessage(String message) {
        try (PrintWriter out = new PrintWriter(new FileWriter("log.txt", true))) {
            out.println(message);
        } catch (Exception e) {
            System.err.println("Error al escribir en el log: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        try {
            java.rmi.registry.LocateRegistry.createRegistry(5000);
            LogServer obj = new LogServer();
            LogInterface stub = (LogInterface) UnicastRemoteObject.exportObject(obj, 0);

            Registry registry = LocateRegistry.getRegistry(5000); 
            registry.rebind("LogServer", stub);

            System.err.println("Servidor listo");
        } catch (Exception e) {
            System.err.println("Excepción del servidor: " + e.toString());
            e.printStackTrace();
        }
    }
}