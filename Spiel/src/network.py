import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.178.103"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.map_data = self.connect()

    def connect(self):
         try:
            self.client.connect(self.addr)
            map_data = self.client.recv(2048*2)  # Empfange die Map-Daten
            return pickle.loads(map_data)  # Map-Daten deserialisieren
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

n = Network()
