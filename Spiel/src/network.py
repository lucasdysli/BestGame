import socket
import pickle
import threading
import pygame

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.178.103"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.server_data = self.connect()
        self.player_id = self.server_data["player_id"]
        self.map_data = {
            "screen_width": self.server_data["screen_width"],
            "screen_height": self.server_data["screen_height"],
            "grid": self.server_data["grid"]
        }
        self.ready_to_move = False

        # Starte einen Thread zum Hören auf Servernachrichten
        self.listen_thread = threading.Thread(target=self.listen_for_server)
        self.listen_thread.start()


    def connect(self):
         try:
            self.client.connect(self.addr)
            server_data = self.client.recv(2048*2)  # Empfange die Server-Daten
            return pickle.loads(server_data)  # Server-Daten deserialisieren
         except:
            pass
    

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)

    def listen_for_server(self):
        # Eine Schleife, die kontinuierlich auf Nachrichten vom Server hört
        running = True 
        while running:
            # Event-Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            try:
                message = self.client.recv(2048).decode("utf-8")
                if message == "ready_to_move":
                    print("Server says:", message)
                    self.ready_to_move = True

            except:
                print("Verbindung zum Server verloren")
                break

    def ready_check(self):
        return self.ready_to_move

    def move_done(self):
        self.ready_to_move = False

    def get_map(self):
        return self.map_data

