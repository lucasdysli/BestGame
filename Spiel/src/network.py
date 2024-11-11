import socket
import pickle

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

    def connect(self):
         try:
            self.client.connect(self.addr)
            server_data = self.client.recv(2048*2)  # Empfange die Server-Daten
            return pickle.loads(server_data)  # Server-Daten deserialisieren
         except:
            pass
    

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)

    def get_map(self):
        return self.map_data

