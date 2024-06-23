import socket
import threading
import random
from py4j.java_gateway import JavaGateway

from format_log import format_log

min_dice = 10
max_dice = 11

gateway = JavaGateway()
log_client = gateway.entry_point

class GameClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.player_id = int(self.client_socket.recv(1024).decode())
        self.listen_port = self.port + self.player_id
        self.dice_rolls = []
        self.in_team = False
        self.is_leader = False
        self.team_members = []
        self.team_inicio = []
        self.team_id = 0
        self.jugando = False
        self.game_id = 1

    def send_message_to_peers(self, message):
        for member in self.team_members:
            try:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((member['IP'], member['PORT']))
                peer_socket.sendall(message.encode())
                peer_socket.close()
            except Exception as e:
                print(f"Failed to send message to {member['IP']}:{member['PORT']}: {e}")

    def listen_for_messages(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.listen_port))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode()
                    print(f"Message from {addr}: {message}")
                    self.handle_message(message)

    def handle_message(self, message):
        #print(f"Mensaje de compañero: {message}")
        if "obtuvo " in message:
            parts = message.split()
            try:
                player_id = int(parts[1])
                dice_value = int(parts[-1])
                if not any(d['player_id'] == player_id for d in self.dice_rolls):
                    self.dice_rolls.append({'player_id': player_id, 'dice_value': dice_value})
                    print(f"Se agregó el dado del jugador {player_id}: {dice_value}")
                else:
                    print(f"El jugador {player_id} envío movimiendo duplicado. Ha sido ignorado.")
            except ValueError:
                print("Error de parsing.")
        elif "listo para iniciar" in message:
            parts = message.split()
            player_id = int(parts[1])
            prop = True
            self.team_inicio.append({'player_id': player_id, 'ready': prop})
            print(f"El jugador {player_id} está listo para empezar el juego.")
        elif "jugada enviada":
            self.dice_rolls = []

    def run(self):
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        self.interactive_loop()

    def interactive_loop(self):
        while True:
            message = input("Ingrese comando: ")
            self.process_command(message)

    def process_command(self, message):
        if message.startswith("unirse") or message.startswith("crear"):
            self.client_socket.send(message.encode())
            response = self.client_socket.recv(1024).decode()
            
            team_id = response[-1]
            game_id = response[-3]
            
            if team_id == '.':
                # ocurrio un error
                print(f"Server response: {response} | OCURRIO UN ERROR")
                return
            
            if "Jugador ya pertenece a equipo." in response:
                print(f"Server response: {response}")
            else:
                log_client.logMessage(format_log('ini', game_id, 'crea-jugador', team_id, self.player_id))
                
                if "Eres lider de equipo" or "se unió como lider del equipo" in response:
                    self.is_leader = True
                    self.in_team = True
                if "se ha unido" in response:
                    self.in_team = True
                print(f"Server response: {response}")
                
                self.game_id = game_id
                self.team_id = team_id
                
                log_client.logMessage(format_log('fin', game_id, 'crea-jugador', team_id, self.player_id))

        elif message == "dado":
            if self.in_team:
                self.roll_dice()
            else:
                print("Debes unirte a un equipo antes de lanzar un dado.")

        elif message == "equipo":
            if self.in_team: 
                self.client_socket.send(message.encode())
                response = self.client_socket.recv(1024).decode()
                self.update_team_members(response)
                print(f"Miembros de equipo actualizados: {self.team_members}")
            else:
                print("Debes pertenecer a un equipo para actualizar a tus miembros de equipo.")

        elif message == "enviar jugada":
            self.send_play()

        elif message == "ver dados":
            self.ver_dados()
            
        elif message == "ver pares":
            if self.in_team: 
                print("Team peers:")
                for peer in self.team_members:
                    print(f"IP: {peer['IP']}, Port: {peer['PORT']}")
            else:
                print("Debes pertenecer a un equipo para ver a los miembros de equipo.")
        
        elif message == "iniciar partida":
            if self.in_team and self.is_leader:
                self.send_start_team()
                response = self.client_socket.recv(1024).decode()
                
                print(f"Servidor: {response}")
            else:
                print("Solo el lider de equipo puede llamar a iniciar la partida.")

        elif message == "iniciar":
            if self.in_team:
                self.start_turn()
            else:
                print("Debes pertenecer a un equipo antes de indicar que estás listo.")

        elif message == "jugador":
            print(f"Cliente: {self.is_leader}")
            self.client_socket.send("lider".encode())
            response = self.client_socket.recv(1024).decode()
            print(f"Servidor: {response}")

        else:
            print("Jugada invalida")
            

    def update_team_members(self, data):
        self.team_members = []
        members_data = data.split(';')  # Asumiendo que los datos vienen separados por ';'
        for member in members_data:
            player_id, ip = member.split(',')
            if int(player_id.strip()) != self.player_id:
                self.team_members.append({'IP': ip.strip(), 'PORT': int(player_id.strip()) + 12345})

    def send_play(self):
        if len(self.dice_rolls) == len(self.team_members) + 1:
            total_dice = sum(d['dice_value'] for d in self.dice_rolls)
            print(f"El valor total es de {total_dice}. Sending to server...")
            self.client_socket.send(f"jugada {total_dice}".encode())
            response = self.client_socket.recv(1024).decode()
            print(f"Server response: {response}")
            if "sumó" in response:
                self.dice_rolls = []
                self.send_message_to_peers("jugada enviada")
        else:
            print("Aun faltan jugadores por lanzar su dado.")

    def send_start_team(self):
        if len(self.team_inicio) == len(self.team_members) + 1:
            print(f"Todos los jugadores listos. Sending to server...")
            self.client_socket.send(f"iniciar partida".encode())
            response = self.client_socket.recv(1024).decode()
            print(f"Server response (3): {response}")
            
        else:
            print("No todos los jugadores están listos para iniciar la partida.")

    def ver_dados(self):
        print("Dice rolls:")
        for roll in self.dice_rolls:
            print(f"El jugador {roll['player_id']} obtuvo un {roll['dice_value']}")

    def ver_inicios(self):
        print("Jugadores listos:")
        for roll in self.team_inicio:
            print(f"Player {roll['player_id']} está listo para iniciar la partida.")

    def roll_dice(self):
        # Verificar si el jugador ya lanzó el dado en este turno
        if any(roll['player_id'] == self.player_id for roll in self.dice_rolls):
            print("Ya has lanzado tu dado este turno.")
        else:
            
            dice_roll = random.randint(min_dice, max_dice)
            print(f"Obtuviste un {dice_roll}.")
            
            # print("dado!, ", self.team_id, self.player_id, dice_roll)
            
            log_client.logMessage(format_log('ini', self.game_id, 'lanza-dado', self.team_id, self.player_id, dice_roll))
            
            self.dice_rolls.append({'player_id': self.player_id, 'dice_value': dice_roll})
            self.send_message_to_peers(f"El jugador {self.player_id} obtuvo un {dice_roll}")
            
            log_client.logMessage(format_log('fin', self.game_id, 'lanza-dado', self.team_id, self.player_id, dice_roll))


    def start_turn(self):
        # Verificar si el jugador ya lanzó 'iniciar' en este turno
        if any(roll['player_id'] == self.player_id for roll in self.team_inicio):
            print("Ya indicaste que estás listo para iniciar la partida.")
        else:
            prop = True
            print(f"Estas listo para iniciar la partida.")
            self.team_inicio.append({'player_id': self.player_id, 'dice_value': prop})
            self.send_message_to_peers(f"El jugador {self.player_id} está listo para iniciar la partida.")

if __name__ == "__main__":
    client = GameClient('localhost', 12345)
    client.run()
