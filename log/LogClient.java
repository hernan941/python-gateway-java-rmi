import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.RemoteException;

public class LogClient {
    private LogInterface logServer;

    public LogClient(String host, int port, String serviceName) {
        try {
            Registry registry = LocateRegistry.getRegistry(host, port);
            logServer = (LogInterface) registry.lookup(serviceName);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void logMessage(String message) {
        try {
            logServer.logMessage(message);
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }
}