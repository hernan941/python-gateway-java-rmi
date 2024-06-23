import socket
import threading
import time
import random
from format_log import format_log

from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
log_client = gateway.entry_point

largo_tablero = 20

class GameServer:
    def __init__(self):
        self.teams = {1: [], 2: []}  # Inicializar con dos equipos vacíos
        self.team_leaders = {}
        self.team_ready = {}
        self.player_info = {}  # Diccionario para almacenar info de jugador: ID, IP, puerto
        self.all_ready = False
        self.lock = threading.Lock()
        self.client_connections = {}  # Diccionario para almacenar conexiones de clientes
        self.equipo_jugando = 0
        self.teams_scores = {1: 0, 2: 0}
        self.winner = 0
        self.start_monitoring()
        self.game_id = self.get_game_id()
        
    def reset_game_state(self):
        """Reinicia el estado del juego para comenzar uno nuevo."""
        self.teams = {1: [], 2: []}  # Reiniciar equipos
        self.team_leaders = {}
        self.team_ready = {}
        self.all_ready = False
        self.equipo_jugando = 0
        self.teams_scores = {1: 0, 2: 0}
        self.winner = 0
        self.game_id = self.game_id + 1  # Opcional: Incrementar ID del juego
            
    def get_game_id(self):
        with open("games.txt", "r") as file:
            content = file.read()
            print(content)
            return int(content)
        
    def set_game_id(self, game_id):
        with open("games.txt", "w") as file:
            file.write(str(game_id))

    def handle_client(self, conn, addr, player_id):
        with self.lock:
            self.player_info[player_id] = {'ip': addr[0], 'port': addr[1]}

        conn.sendall(f"{player_id}".encode())
        print(f"Jugador {player_id} conectado desde {addr}")

        try:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break  # Si no hay datos, el cliente se desconectó

                if data.startswith("unirse"):
                    parts = data.split()
                    if len(parts) == 2:
                        response, is_leader = self.join_team(int(parts[1]), player_id)
                        leader_status = "Eres lider de equipo." if is_leader else "No eres lider de equipo."
                        response = leader_status + " | " +  response
                        conn.sendall(response.encode())
                    else:
                        conn.sendall("Comando en formato invalido".encode())
                else:
                    response = self.process_command(data, player_id)
                    conn.sendall(response.encode())

                    #if self.all_ready:
                    #    self.broadcast_all("Ahora si hijos de su chingada madre.")
                    #    self.all_ready = False

        except Exception as e:
            print(f"Error with player {player_id}: {e}")
        finally:
            with self.lock:
                # El código proporcionado para manejar la desconexión
                team_id = None
                for tid, members in self.teams.items():
                    if player_id in members:
                        team_id = tid
                        break
                
                if team_id is not None and self.team_leaders.get(team_id) == player_id:
                    self.teams[team_id].remove(player_id)
                    if self.teams[team_id]:
                        new_leader = self.teams[team_id][0]
                        self.team_leaders[team_id] = new_leader
                        print(f"Nuevo líder del equipo {team_id}: Jugador {new_leader}")
                    else:
                        del self.teams[team_id]
                        del self.team_leaders[team_id]
                        print(f"El equipo {team_id} ha sido disuelto por falta de miembros.")
                elif team_id is not None:
                    self.teams[team_id].remove(player_id)
                
                del self.player_info[player_id]
                if conn in self.client_connections:
                    del self.client_connections[conn]
            print(f"Jugador {player_id} se desconectó.")

    def process_command(self, command, player_id):
        parts = command.split()
        cmd = parts[0]

        if cmd == "unirse" and len(parts) == 2 and not self.player_in_any_team(player_id):
            return self.join_team(int(parts[1]), player_id)
        elif cmd == "crear" and not self.player_in_any_team(player_id):
            return self.create_team(player_id)
        elif command == "iniciar partida":
            return self.start_game(player_id)
        elif cmd == "jugada" and len(parts) == 2:
            team_id = self.get_team_by_player_id(player_id)
            if team_id == self.equipo_jugando:
                return self.record_play(int(parts[1]), player_id)
            else:
                return "No es tu turno de jugar."
        elif cmd == "equipo":
            return self.list_team_members(player_id)
        elif cmd == "lider":
            if player_id in self.team_leaders.values():
                print(self.team_leaders)
                return "Eres lider"
            else:
                return "No eres lider"
            
        else:
            return "Invalid command"
        
    def start_monitoring(self):
        threading.Thread(target=self.monitoring_loop, daemon=True).start()

    def monitoring_loop(self):
        while True:
            if self.winner != 0:
                log_client.logMessage(format_log('ini', self.game_id, 'fin-juego'))
                self.broadcast_all(f"Se ha acabado la partida, el equipo ganador es {self.winner}")
                
                self.reset_game_state()
                
                time.sleep(5)  # Esperar un poco antes de comenzar a monitorear el nuevo juego
                log_client.logMessage(format_log('fin', self.game_id, 'fin-juego'))
                
                self.set_game_id(self.game_id)  # Guardar el nuevo ID del juego
                
                
            print("Monitoring...")
            time.sleep(5)  # Check every 5 seconds

    def list_team_members(self, player_id):
        for team_id, members in self.teams.items():
            if player_id in members:
                member_info = [f"{member}, {self.player_info[member]['ip']}" for member in members]
                return ';'.join(member_info)
        return "You are not in a team"


    def player_in_any_team(self, player_id):
        return any(player_id in team for team in self.teams.values())

    def join_team(self, team_id, player_id):
        if team_id in self.teams and player_id not in self.teams[team_id]:
            self.teams[team_id].append(player_id)
            is_leader = False  # Flag para identificar si el jugador es el líder
            if len(self.teams[team_id]) == 1:
                self.team_leaders[team_id] = player_id
                is_leader = True
            return f"El jugador {player_id} se ha unido al equipo {self.game_id}-{team_id}", is_leader
        return "ID invalido o ya pertenece a equipo.", False

    def create_team(self, player_id):
        if self.player_in_any_team(player_id):
            return "Jugador ya pertenece a equipo."
        
        with self.lock:
            new_team_id = max(self.teams) + 1
            self.teams[new_team_id] = [player_id]
            self.teams[new_team_id].append(player_id)
            self.team_leaders[new_team_id] = player_id
            self.teams_scores[new_team_id] = 0
            return f"El jugador {player_id} se unió como lider del equipo {self.game_id}-{new_team_id}"
        
    def get_team_by_player_id(self, player_id):
        # Iterar sobre los pares clave-valor en self.team_leaders
        for team_id, leader_id in self.team_leaders.items():
            if leader_id == player_id:
                return team_id
        return None  

    def start_game(self, player_id):
        team_id = self.get_team_id_for_leader(player_id)
        if team_id:
            self.team_ready[team_id] = True
            if all(self.team_ready.get(tid, False) for tid in self.teams):
                log_client.logMessage(format_log('ini', self.game_id, 'inicio-juego'))
                
                self.all_ready = True

                self.equipo_jugando = random.choice(list(self.teams.keys()))
                self.broadcast_all(f"Se ha iniciado la partida! Juega el equipo {self.equipo_jugando}")
                
                log_client.logMessage(format_log('fin', self.game_id, 'inicio-juego'))

                return "Todos los equipos están listos. El juego comienza."
            
            return f"El equipo {team_id} liderado por el jugador {player_id} está listo."
        return "No eres lider o el equipo es invalido."
    
    def get_next_team(self, current_team):
        team_ids = sorted(self.teams.keys())
        current_index = team_ids.index(current_team)
        next_index = (current_index + 1) % len(team_ids)
        return team_ids[next_index]
    
    def get_team_id_for_leader(self, player_id):
        for team_id, leader in self.team_leaders.items():
            if leader == player_id:
                return team_id
        return None
    
    def broadcast_all(self, message):
        for conn in self.client_connections:
            try:
                conn.sendall(message.encode())
            except Exception as e:
                print("Fallo de comunicación:", e)

    def record_play(self, score, player_id):
        current_team = self.equipo_jugando
        next_team = self.get_next_team(current_team)
        if player_id == self.team_leaders.get(player_id) and 1 <= score <= 30:
            self.teams_scores[current_team] += score
            if self.teams_scores[current_team] >= largo_tablero:
                self.winner = current_team
            self.equipo_jugando = next_team
            return f"El equipo {current_team} sumó {score}"
        return "Comando invalido"

    def run_server(self):
        host = 'localhost'
        port = 12345
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()
        print("Server is listening for connections...")

        player_count = 0

        while True:
            conn, addr = server_socket.accept()
            player_count += 1
            self.client_connections[conn] = {
            'player_id': player_count,
            'socket': conn
        }
            thread = threading.Thread(target=self.handle_client, args=(conn, addr, player_count))
            thread.start()

if __name__ == "__main__":
    server = GameServer()
    server.run_server()
