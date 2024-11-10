import socket
from _thread import *
import sys
import random
from src.map import Map
import pickle

server = "192.168.178.103"
port = 5555


class Server:
    def __init__(self, width=800, height=600):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.s.bind((server, port))
        except socket.error as e:
            str(e)

        self.s.listen(12) #maximale Anzahl an Spielern die zum Server connecten können

        print("Server gestartet")

        # Initialisiere die Map-Daten
        self.screen_width = width
        self.screen_height = height
        self.tile_size = 64  # Größe eines Tiles (Felds)
        
        # Berechne die Anzahl der Tiles in beiden Dimensionen
        self.grid_width = self.screen_width // self.tile_size
        self.grid_height = self.screen_height // self.tile_size
        
        # Erstelle das 2D-Grid mit zufälligen 'mountain' oder 'grass' Einträgen
        self.grid = [[random.choice(['mountain', 'grass']) for _ in range(self.grid_width)] for _ in range(self.grid_height)]



    def start_server(self):
        # Endlosschleife zum Warten auf Verbindungen und Starten neuer Threads
        while True:
            conn, addr = self.s.accept()
            print("Verbunden mit:", addr)
            start_new_thread(self.threaded_client, (conn,))

    def threaded_client(self, conn):
        # Verpacke die Map-Daten
        map_data = {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "grid": self.grid
        }
        conn.send(pickle.dumps(map_data))  # Serialisierte Map-Daten senden
        conn.send(str.encode("Connected"))
        reply = ""
        while True:
            try:
                data = conn.recv(2048)
                reply = data.decode("utf-8")

                if not data:
                    print("Disconnected")
                    break
                else:
                    print("Received: ", reply)
                    print("Sending: ", reply)

                conn.sendall(str.encode(reply))
            except:
                break
    """     print("Connection lost")
        conn.close() """

# Server-Instanz erstellen und starten
if __name__ == "__main__":
    server = Server()
    server.start_server()



