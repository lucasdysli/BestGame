import socket
import pickle
import threading
import pygame
import copy

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
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
        self.player_positions_dic = {}
        self.weak_player = False
        self.player_information_dic = {}
        self.player_positions_dic = {}
        self.player_health_dic = {}
        self.death = False

        #Variable damit der Listening Thread abgebrochen werden kann
        self.running = True

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
            #return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)

    def listen_for_server(self):
        # Eine Schleife, die kontinuierlich auf Nachrichten vom Server hört
        while self.running:
            # Event-Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            try:
                # Empfange und deserialisiere die Nachricht vom Server
                data = self.client.recv(2048)
                message = pickle.loads(data)

                #print("Empfangene Nachricht:", message)
                
                # Verarbeite die Nachricht basierend auf dem Typ
                if message.get("type") == "ready_to_move":
                    self.ready_to_move = True

                elif message.get("type") == "player_information":
                    self.player_information_dic = message["data"]
                    self.player_last_position_dic = copy.deepcopy(self.player_positions_dic)
                    self.player_positions_dic = {player_id: player_info["position"] 
                                        for player_id, player_info in self.player_information_dic.items()}
                    self.player_life_points_dic = {player_id: player_info["life_points"]
                                        for player_id, player_info in self.player_information_dic.items()}
                    
                elif message.get("type") == "death_message":
                    self.death = True

            except Exception as e:
                print("Verbindung zum Server verloren:", str(e))
                break

    def ready_check(self):
        return self.ready_to_move

    def move_done(self):
        self.ready_to_move = False

    def get_map(self):
        return self.map_data

    def stop(self):
        self.running = False
        self.listen_thread.join()
