import socket
import time
from _thread import *
import sys
import random
import threading
import pickle
import select
import copy

server = "127.0.0.1"
port = 5555


class Server:
    def __init__(self, width=1000, height=700, move_delay=4):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_count = 0  # Zählvariable für die Spieler-IDs
        self.move_delay = move_delay
        self.last_move_time = time.time()
        self.player_information_dic = {}
        self.last_player_information_dic = {}
        self.ready_to_move = False
        self.move_message_send = False
        self.condition = threading.Condition()
        self.clients_ready = 0
        self.weak_players = {}
        self.enemy_selection_dic ={}
        self.attacked_players_dic ={}
        self.life_bar_dic = {}


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
            ["m1", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m3"],
            ["m4", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m4"],
            ["m4", "g", "g", "g", "t", "g", "g", "g", "g", "g", "t", "t", "g", "g", "t", "g", "g", "g", "t", "g", "t", "t", "t", "g", "g", "g", "t", "g", "g", "g", "m4"],
            ["m4", "g", "g", "g", "g", "t", "g", "t", "g", "g", "t", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "t", "g", "g", "g", "g", "t", "g", "g", "g", "m4"],
            ["m4", "g", "t", "t", "g", "t", "g", "g", "t", "g", "t", "t", "g", "t", "t", "g", "g", "g", "g", "g", "t", "t", "g", "t", "g", "g", "g", "t", "g", "g", "m4"],
            ["m4", "g", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m4"],
            ["m4", "t", "t", "t", "g", "g", "t", "g", "g", "g", "g", "g", "t", "g", "t", "g", "g", "g", "g", "g", "t", "g", "g", "g", "t", "g", "g", "t", "t", "g", "m4"],
            ["m4", "g", "g", "t", "t", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "g", "t", "g", "g", "t", "m4"],
            ["m4", "g", "g", "g", "t", "g", "t", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "t", "g", "g", "t", "g", "t", "g", "t", "t", "m4"],
            ["m4", "g", "g", "g", "g", "t", "g", "g", "g", "t", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "g", "t", "g", "t", "g", "g", "g", "g", "t", "m4"],
            ["m4", "g", "g", "g", "g", "g", "g", "g", "g", "t", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "t", "g", "t", "g", "g", "g", "g", "g", "m4"],
            ["m4", "g", "t", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "t", "g", "g", "g", "g", "g", "t", "g", "t", "m4"],
            ["m4", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "t", "g", "g", "g", "g", "g", "t", "t", "t", "m4"],
            ["m4", "g", "g", "g", "t", "g", "t", "g", "g", "g", "t", "g", "g", "g", "g", "t", "t", "t", "g", "t", "g", "g", "g", "g", "g", "t", "g", "t", "g", "g", "m4"],
            ["m4", "g", "g", "g", "g", "t", "g", "g", "t", "t", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "t", "t", "g", "g", "t", "g", "g", "t", "g", "g", "m4"],
            ["m4", "t", "t", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "t", "t", "g", "t", "g", "g", "t", "g", "g", "g", "g", "t", "t", "t", "g", "t", "t", "m4"],
            ["m4", "t", "g", "g", "g", "g", "g", "t", "t", "g", "g", "g", "t", "g", "g", "g", "g", "t", "g", "t", "t", "g", "g", "g", "g", "g", "g", "g", "g", "t", "m4"],
            ["m4", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "m4"],
            ["m4", "g", "g", "t", "g", "t", "g", "g", "g", "g", "t", "g", "g", "g", "g", "g", "g", "g", "g", "g", "t", "g", "g", "g", "g", "t", "g", "g", "g", "g", "m4"],
            ["m4", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m2", "m4"],
            ["m6", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m5", "m7"],
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

        # 1. Führe Positionsabgleiche durch und aktualisiere self.weak_players
        self.weak_players = self.handle_position_swaps()

        # 2. Bearbeite Kollisionsfälle und erweitere self.weak_players bei Bedarf
        self.weak_players = self.handle_collisions(self.weak_players)

    def handle_position_swaps(self):
        # Alle Spieler, die nicht auf das Ziel-Feld kommen, werden hier gespeichert
        for player_1, player_1_info in self.last_player_information_dic.items():
            for player_2, player_2_info in self.last_player_information_dic.items():
                pos_1_last = player_1_info["position"]
                pos_2_last = player_2_info["position"]


                # Überspringe den Vergleich eines Spielers mit sich selbst
                if player_1 == player_2:
                    continue
                
                # Check, ob Spieler 1 auf dem letzten Standort von Spieler 2 steht
                pos_2_current = self.player_information_dic.get(player_2)["position"]
                pos_1_current = self.player_information_dic.get(player_1)["position"]

                
                if pos_1_current == pos_2_last:
                    # Prüfe, ob der aktuelle Standort von Spieler 2 der letzte Standort von Spieler 1 ist
                    if pos_2_current == pos_1_last:
                        # Speichere das Spielerpaar in weak_players
                        self.weak_players[player_1] = pos_1_last
                        self.weak_players[player_2] = pos_2_last

        # Aktualisiere die Positionen der weak_players
        for weak_player in self.weak_players:
            # Setze die Position des weak_players auf seine letzte Position zurück
            self.player_information_dic[weak_player]["position"] = self.last_player_information_dic[weak_player]["position"]

        return self.weak_players


    def collision_check(self):
        positions = {}
        for player_id, player_info in self.player_information_dic.items():
            position = (player_info['position']['x'], player_info['position']['y'])
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
                    if self.player_information_dic[player]["position"] == self.last_player_information_dic[player]["position"]:
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
            self.player_information_dic[weak_player]["position"] = self.last_player_information_dic[weak_player]["position"]

        return weak_players

    def fight_time(self):
        # Dictionary zum Speichern der Spieler, die angegriffen werden
        attacked_players = {}
        # Durchlaufe alle Spieler und ihre ausgewählten Gegner
        for attacker_id, selected_enemy_id in self.enemy_selection_dic.items():
            if not selected_enemy_id:
                continue             
            attacker_pos = self.player_information_dic.get(attacker_id)["position"]
            enemy_pos = self.player_information_dic.get(selected_enemy_id)["position"]

            # Prüfe, ob die Positionen von Angreifer und Gegner verfügbar sind
            if attacker_pos and enemy_pos:
                # Berechne die horizontale und vertikale Distanz
                distance_x = abs(attacker_pos["x"] - enemy_pos["x"])
                distance_y = abs(attacker_pos["y"] - enemy_pos["y"])

                # Überprüfe, ob der Gegner in einem der 9 Felder um den Angreifer steht
                if distance_x <= 1 and distance_y <= 1:
                    # Füge den Angriff hinzu
                    if selected_enemy_id not in attacked_players:
                        attacked_players[selected_enemy_id] = []
                    attacked_players[selected_enemy_id].append(attacker_id)

                    if "life_points" in self.player_information_dic[selected_enemy_id]:
                        self.player_information_dic[selected_enemy_id]["life_points"] -= 20    
                        






    def threaded_client(self, conn):
        # Inkrementiere eine Zählvariable und weise eine Spieler-ID zu
        self.player_count += 1
        player_id = self.player_count
        death = False
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

        # Initialisiere `player_information_dic` mit Lebenspunkten und Position
        self.player_information_dic[player_id] = {"position": {"x": 0, "y": 0}, "life_points": 100}

        #BEGINN DER EIGNELTICHEN SCHLEIFE
        while True:

            if self.ready_check():
                message = {"type": "ready_to_move"}
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
                        self.player_count -= 1
                        break
                    data_deserialised = pickle.loads(data)
                    
                    #Überprüfe ob es sich um eine Gegnerauswahl handelt
                    if data_deserialised.get("type") == "enemy_selection" and death == False:
                        print("Spieler:", player_id, "wählt:", data_deserialised["selected_enemy"])
                        self.enemy_selection_dic[player_id]= data_deserialised["selected_enemy"]                        


                    # Überprüfe, ob es sich um eine Positionsnachricht handelt
                    if data_deserialised.get("type") == "position":
                        # Speichere die Position des Spielers im Dictionary unter der player_id   
                        self.player_information_dic[player_id]["position"] = {
                            "x": data_deserialised["x"],
                            "y": data_deserialised["y"]
                        }

                        #Sammelpunkt für alle Clients bevor mit Positionen gestartet wird
                        with self.condition:
                            self.clients_ready += 1
                            # Wenn alle Clients bereit sind, können sie fortfahren
                            if self.clients_ready == self.player_count:
                                self.perform_collision_check() #Nur der letzte Thread gibt diese Funktion frei
                                self.fight_time()
                                self.condition.notify_all()  # Alle wartenden Clients freigeben
                                self.clients_ready = 0  # Zurücksetzen für den nächsten Sammelpunkt
                            else:
                                self.condition.wait()  # Warten, bis alle Clients bereit sind

                        self.last_player_information_dic = copy.deepcopy(self.player_information_dic)

                        #Überprüfung ob Spieler gestorben ist
                        if self.player_information_dic[player_id]["life_points"] <= 0 and death == False:
                            message = {
                            "type": "death_message",
                            }
                            conn.send(pickle.dumps(message))  
                            death = True  
                            self.player_information_dic[player_id]["position"] = {
                                "x": 0,
                                "y": 0
                            }


                        #Neue Positionen an Clients zurückschicken
                        print("Positionen werden geschickt:", player_id)
                        message = {
                            "type": "player_information",
                            "data": self.player_information_dic
                        }
                        conn.send(pickle.dumps(message))
                        time.sleep(0.1)

                except Exception as e:
                    print(f"Fehler bei Spieler {player_id}: {e}")
                    self.player_count -= 1
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



