import java.rmi.Remote;
import java.rmi.RemoteException;

public interface LogInterface extends Remote {
    void logMessage(String message) throws RemoteException;
}