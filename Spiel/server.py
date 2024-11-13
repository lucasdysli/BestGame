import socket
import time
from _thread import *
import sys
import random
import threading
import pickle
import select
import copy

server = "192.168.178.103"
port = 5555


class Server:
    def __init__(self, width=1000, height=700, move_delay=2):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_count = 0  # Zählvariable für die Spieler-IDs
        self.move_delay = move_delay
        self.last_move_time = time.time()
        self.player_positions_dic = {}
        self.last_player_positions_dic = {}
        self.ready_to_move = False
        self.move_message_send = False
        self.condition = threading.Condition()
        self.clients_ready = 0
        self.weak_players = {}

        # Starte den Timer in einem separaten Thread
        timer_thread = threading.Thread(target=self.timer_func)  # <--- Timer-Thread erstellen  
        timer_thread.daemon = True  # <--- Setze den Timer-Thread auf Daemon-Modus
        timer_thread.start()  # <--- Starte den Timer-Thread

        try:
            self.s.bind((server, port))
        except socket.error as e:
            str(e)

        self.s.listen(12) #maximale Anzahl an Spielern die zum Server connecten können

        print("Server gestartet")

        # Initialisiere die Map-Daten
        self.screen_width = width
        self.screen_height = height
        self.tile_size = 32  # Größe eines Tiles (Felds)
        
        # Berechne die Anzahl der Tiles in beiden Dimensionen
        self.grid_width = self.screen_width // self.tile_size
        self.grid_height = self.screen_height // self.tile_size
        
        # Erstelle das 2D-Grid mit 'mountain' oder 'grass' Einträgen
        self.grid = [
            ["m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m"],
            ["m", "g", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m"],
            ["m", "g", "m", "g", "m", "g", "g", "g", "g", "g", "m", "m", "g", "g", "m", "g", "g", "g", "m", "g", "m", "m", "m", "g", "g", "g", "m", "g", "g", "g", "m"],
            ["m", "g", "g", "g", "g", "m", "g", "m", "g", "g", "m", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m", "g", "g", "g", "m"],
            ["m", "g", "m", "m", "g", "m", "g", "g", "m", "g", "m", "m", "g", "m", "m", "g", "g", "g", "g", "g", "m", "m", "g", "m", "g", "g", "g", "m", "g", "g", "m"],
            ["m", "g", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m"],
            ["m", "m", "m", "m", "g", "g", "m", "g", "g", "g", "g", "g", "m", "g", "m", "g", "g", "g", "g", "g", "m", "g", "g", "g", "m", "g", "g", "m", "m", "g", "m"],
            ["m", "g", "g", "m", "m", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "m", "g", "g", "m", "m"],
            ["m", "g", "g", "g", "m", "g", "m", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "m", "g", "g", "m", "g", "m", "g", "m", "m", "m"],
            ["m", "g", "g", "g", "g", "m", "g", "g", "g", "m", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "m", "g", "m", "g", "g", "g", "g", "m", "m"],
            ["m", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "m", "g", "m", "g", "g", "g", "g", "g", "m"],
            ["m", "g", "m", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "m", "g", "g", "g", "g", "g", "m", "g", "m", "m"],
            ["m", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "m", "g", "g", "g", "g", "g", "m", "m", "m", "m"],
            ["m", "g", "g", "g", "m", "g", "m", "g", "g", "g", "m", "g", "g", "g", "g", "m", "m", "m", "g", "m", "g", "g", "g", "g", "g", "m", "g", "m", "g", "g", "m"],
            ["m", "g", "g", "g", "g", "m", "g", "g", "m", "m", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "m", "m", "g", "g", "m", "g", "g", "m", "g", "g", "m"],
            ["m", "m", "m", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m", "m", "g", "m", "g", "g", "m", "g", "g", "g", "g", "m", "m", "m", "g", "m", "m", "m"],
            ["m", "m", "g", "g", "g", "g", "g", "m", "m", "g", "g", "g", "m", "g", "g", "g", "g", "m", "g", "m", "m", "g", "g", "g", "g", "g", "g", "g", "g", "m", "m"],
            ["m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m"],
            ["m", "g", "g", "m", "g", "m", "g", "g", "g", "g", "m", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m"],
            ["m", "m", "g", "g", "m", "g", "g", "g", "m", "m", "m", "m", "g", "g", "m", "g", "g", "m", "g", "m", "g", "g", "g", "g", "g", "m", "g", "g", "g", "g", "m"],
            ["m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m"],
        ]



    def start_server(self):
        # Endlosschleife zum Warten auf Verbindungen und Starten neuer Threads
        while True:
            conn, addr = self.s.accept()
            print("Verbunden mit:", addr)
            start_new_thread(self.threaded_client, (conn,))

    def timer_func(self):
        while True:
            # Überprüfen, ob 5 Sekunden vergangen sind und die Bewegung ausgeführt werden soll
            current_time = time.time()
            if current_time - self.last_move_time >= self.move_delay:
                self.ready_to_move = True
                self.last_move_time = time.time()  # Setze den Timer zurück
            else:
                time.sleep(0.01)
    
    def ready_check(self):
        return self.ready_to_move

    def perform_collision_check(self):
        # Leere self.weak_players für diesen Zyklus
        self.weak_players = {}

        print("Neue Pos:", self.player_positions_dic)
        print("Alte Pos:", self.last_player_positions_dic)

        # 1. Führe Positionsabgleiche durch und aktualisiere self.weak_players
        self.weak_players = self.handle_position_swaps()

        # 2. Bearbeite Kollisionsfälle und erweitere self.weak_players bei Bedarf
        self.weak_players = self.handle_collisions(self.weak_players)

    def handle_position_swaps(self):
        # Alle Spieler, die nicht auf das Ziel-Feld kommen, werden hier gespeichert
        for player_1, pos_1_last in self.last_player_positions_dic.items():
            for player_2, pos_2_last in self.last_player_positions_dic.items():

                # Überspringe den Vergleich eines Spielers mit sich selbst
                if player_1 == player_2:
                    continue
                
                # Check, ob Spieler 1 auf dem letzten Standort von Spieler 2 steht
                pos_2_current = self.player_positions_dic.get(player_2)
                pos_1_current = self.player_positions_dic.get(player_1)
                
                if pos_1_current == pos_2_last:
                    # Prüfe, ob der aktuelle Standort von Spieler 2 der letzte Standort von Spieler 1 ist
                    if pos_2_current == pos_1_last:
                        # Speichere das Spielerpaar in weak_players
                        self.weak_players[player_1] = pos_1_last
                        self.weak_players[player_2] = pos_2_last

        # Aktualisiere die Positionen der weak_players
        for weak_player in self.weak_players:
            # Setze die Position des weak_players auf seine letzte Position zurück
            self.player_positions_dic[weak_player] = self.last_player_positions_dic[weak_player]

        return self.weak_players


    def collision_check(self):
        positions = {}
        for player_id, pos in self.player_positions_dic.items():
            position = (pos['x'], pos['y'])
            if position in positions:
                positions[position].append(player_id)
            else:
                positions[position] = [player_id]

        # Ausgabe der Spieler, die auf derselben Position stehen
        collisions = {pos: players for pos, players in positions.items() if len(players) > 1}
        return collisions
            
    def handle_collisions(self, weak_players):
        
        # Rufe Kollisionsdaten ab
        collisions = self.collision_check()
        
        if collisions:
            for pos, players in collisions.items():
                # Prüfe, ob ein Spieler bereits vorher auf dem Feld war
                staying_player = None
                for player in players:
                    # Spieler steht bereits auf dem Feld und darf bleiben
                    if self.player_positions_dic[player] == self.last_player_positions_dic[player]:
                        staying_player = player
                        break

                if staying_player:
                    # Wenn ein Spieler bleiben darf, sind alle anderen "weak_players"
                    for player in players:
                        if player != staying_player:
                            self.weak_players[player] = pos

                else:
                    # Falls kein Spieler vorher auf dem Feld war, wähle zufällig einen, der bleiben darf
                    staying_player = random.choice(players)
                    for player in players:
                        if player != staying_player:
                            self.weak_players[player] = pos


        # Aktualisiere die Positionen der weak_players
        for weak_player in weak_players:
            # Setze die Position des weak_players auf seine letzte Position zurück
            self.player_positions_dic[weak_player] = self.last_player_positions_dic[weak_player]

        return weak_players





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
        time.sleep(0.1)

        #BEGINN DER EIGNELTICHEN SCHLEIFE
        while True:

            if self.ready_check():
                message = {"type": "ready_to_move"}
                print("ready to move:", player_id)
                conn.send(pickle.dumps(message))
                #Sammelpunkt für alle Clients bevor mit Positionen gestartet wird
                with self.condition:
                    self.clients_ready += 1
                    # Wenn alle Clients bereit sind, können sie fortfahren
                    if self.clients_ready == self.player_count:
                        self.ready_to_move = False
                        self.condition.notify_all()  # Alle wartenden Clients freigeben
                        self.clients_ready = 0  # Zurücksetzen für den nächsten Sammelpunkt
                    else:
                        self.condition.wait()  # Warten, bis alle Clients bereit sind


            # Überprüfen, ob Daten verfügbar sind, bevor `recv` aufgerufen wird, sonst Dauerschleife
            readable, _, _ = select.select([conn], [], [], 0.1)  
            if readable:
                try:
                    data = conn.recv(2048)
                    if not data:
                        print("Spieler", player_id, "disconnected")
                        break
                    data_deserialised = pickle.loads(data)
                    

                    # Überprüfe, ob es sich um eine Positionsnachricht handelt
                    if data_deserialised.get("type") == "position":
                        # Speichere die Position des Spielers im Dictionary unter der player_id
                        self.player_positions_dic[player_id] = {
                            "x": data_deserialised["x"],
                            "y": data_deserialised["y"]
                        }

                        #Sammelpunkt für alle Clients bevor mit Positionen gestartet wird
                        with self.condition:
                            self.clients_ready += 1
                            # Wenn alle Clients bereit sind, können sie fortfahren
                            if self.clients_ready == self.player_count:
                                self.perform_collision_check() #Nur der letzte Thread gibt diese Funktion frei
                                self.condition.notify_all()  # Alle wartenden Clients freigeben
                                self.clients_ready = 0  # Zurücksetzen für den nächsten Sammelpunkt
                            else:
                                self.condition.wait()  # Warten, bis alle Clients bereit sind


                        if player_id in self.weak_players:
                            # Code ausführen, falls player_id ein schwacher Spieler ist
                            print(f"Spieler {player_id} ist ein weak_player.")
                            message = {"type": "weak_player"}
                            conn.send(pickle.dumps(message))
                            time.sleep(0.1)

                        self.last_player_positions_dic = copy.deepcopy(self.player_positions_dic)
                        print("Alte Positionen werden geupdated", self.last_player_positions_dic)

                        #Neue Positionen an Clients zurückschicken
                        message = {
                            "type": "player_positions",
                            "data": self.player_positions_dic
                        }
                        conn.send(pickle.dumps(message))
                        time.sleep(0.1)

                except Exception as e:
                    print(f"Fehler bei Spieler {player_id}: {e}")
                    break
            else:
                # Wenn keine Daten verfügbar sind, eine kurze Pause einfügen, um CPU-Auslastung zu verringern
                time.sleep(0.01)

    """     print("Connection lost")
        conn.close() """

# Server-Instanz erstellen und starten
if __name__ == "__main__":
    server = Server()
    server.start_server()



