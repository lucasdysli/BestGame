# src/game.py

import pygame
import time
import random
import socket
import time
from src.map import Map
from src.player import Player
from src.network import Network

class Game:
    def __init__(self, network):
        
        self.network = network
        self.move_direction = None  
        self.player_positions_dic = {}
        self.last_x_pos = ""
        self.last_y_pos = ""

        # Map-Daten von der Network-Instanz abrufen
        map_data = network.get_map()

        # Map-Daten speichern
        self.screen_width = map_data["screen_width"]
        self.screen_height = map_data["screen_height"]
        self.tile_size = 32  # Größe eines Tiles (Felds)
        self.grid = map_data["grid"]  # Das 2D-Grid mit 'mountain' und 'grass'
        
        # Initialisiere das Pygame-Fenster
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Mein Spiel mit Runden")
        self.clock = pygame.time.Clock()
                
        # Erstelle die Map
        self.map = Map(self.screen_width // self.tile_size, self.screen_height // self.tile_size, self.tile_size, self.grid)
        
        # Spieler-Startposition auf einem grünen Wiesenfeld setzen
        self.start_x = 544 - self.network.player_id * self.tile_size
        self.start_y = 256
        self.player = Player(self.start_x, self.start_y, self.tile_size, self.map)


    def create_player_on_grass_field(self):
        # Suche zufällig ein Wiesenfeld ('grass')
        while True:
            x = random.randint(0, self.screen_width // self.tile_size - 1)
            y = random.randint(0, self.screen_height // self.tile_size - 1)
            if self.map.get_tile_type(x * self.tile_size, y * self.tile_size) == 'g':
                # Berechne die Position basierend auf der Feldgröße
                start_x = x * self.tile_size
                start_y = y * self.tile_size
                return Player(start_x, start_y, self.tile_size, self.map)

    def run(self):
        running = True
        while running:
            # Event-Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Tastenstatus abfragen
            keys = pygame.key.get_pressed()

            #Führe die Bewegung aus, sobald Server sendet
            if self.network.ready_check():
                self.player.move(self.move_direction)  # Führe die Bewegung aus
                self.network.move_done()

                #Melde neue Position zurück an den Server und hole die Positionen der restlichen Spieler
                x, y = self.player.get_position()
                own_position = {"type": "position", "x": x, "y": y}
                self.network.send(own_position)
                time.sleep(0.5)
                if self.network.weak_player:
                    print("weak")
                    self.player.x = self.last_x_pos
                    self.player.y = self.last_y_pos
                    self.network.weak_player = False
                
                self.last_x_pos = self.player.x
                self.last_y_pos = self.player.y

                # Bildschirm aktualisieren
                self.screen.fill((255, 255, 255))  # Hintergrundfarbe weiß           
                self.map.draw(self.screen)  # Zeichne die Map  
                self.player.draw(self.screen, self.network.player_positions_dic)  # Zeichne die Spielfiguren
                pygame.display.flip()
                self.clock.tick(60)  # 60 FPS
            
            # Spiellogik: Warte auf eine Eingabe für die Richtung
            if keys[pygame.K_LEFT]:
                self.move_direction = "left"
            elif keys[pygame.K_RIGHT]:
                self.move_direction = "right"
            elif keys[pygame.K_UP]:
                self.move_direction = "up"
            elif keys[pygame.K_DOWN]:
                self.move_direction = "down"
            time.sleep(0.1)

        self.network.stop()
        pygame.quit()


