import socket
import time
from _thread import *
import sys
import random
from src.map import Map
import pickle

server = "192.168.178.103"
port = 5555


class Server:
    def __init__(self, width=800, height=600, move_delay=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_count = 0  # Zählvariable für die Spieler-IDs
        self.move_delay = move_delay
        self.last_move_time = time.time()

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
        # Inkrementiere eine Zählvariable und weise eine Spieler-ID zu
        self.player_count += 1
        player_id = self.player_count
        print(f"Spieler {player_id} verbunden.")

        # Verpacke die Server-Daten
        server_data = {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "grid": self.grid,
            "player_id": player_id  # Spieler-ID hinzufügen
        }
        conn.send(pickle.dumps(server_data))  # Serialisierte Server-Daten senden

        conn.setblocking(False)  # Setze den Socket in den nicht-blockierenden Modus

        while True:
            # Überprüfen, ob 5 Sekunden vergangen sind und die Bewegung ausgeführt werden soll
            current_time = time.time()
            if current_time - self.last_move_time >= self.move_delay:
                conn.send(str.encode("ready_to_move"))
                print("gesendet")
                self.last_move_time = time.time()  # Setze den Timer zurück
            else:
                time.sleep(0.1)
                
            try:
                data = conn.recv(2048)
                data_deserialised = pickle.loads(data)
                
                if not data:
                    print("Spieler", player_id, "disconnected")
                    break
                else:
                    print("Received: ", data_deserialised)
                    print("Sending: ", data_deserialised)

                """ conn.sendall(str.encode(reply)) """

            except BlockingIOError:
                # Keine Daten verfügbar, weiter zum nächsten Schleifendurchlauf
                continue

            except:
                continue
    """     print("Connection lost")
        conn.close() """

# Server-Instanz erstellen und starten
if __name__ == "__main__":
    server = Server()
    server.start_server()



