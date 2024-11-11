# src/game.py

import pygame
import time
import random
import socket
from src.map import Map
from src.player import Player
from src.network import Network

class Game:
    def __init__(self, network):
        
        self.network = network
        self.move_direction = None  # Variable für die Bewegungsrichtung

        # Map-Daten von der Network-Instanz abrufen
        map_data = network.get_map()

        # Map-Daten speichern
        self.screen_width = map_data["screen_width"]
        self.screen_height = map_data["screen_height"]
        self.tile_size = 64  # Größe eines Tiles (Felds)
        self.grid = map_data["grid"]  # Das 2D-Grid mit 'mountain' und 'grass'
        
        # Initialisiere das Pygame-Fenster
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Mein Spiel mit Runden")
        self.clock = pygame.time.Clock()
                
        # Erstelle die Map
        self.map = Map(self.screen_width // self.tile_size, self.screen_height // self.tile_size, self.tile_size, self.grid)
        
        # Spieler-Startposition auf einem grünen Wiesenfeld setzen
        self.player = self.create_player_on_grass_field()


    def create_player_on_grass_field(self):
        # Suche zufällig ein Wiesenfeld ('grass')
        while True:
            x = random.randint(0, self.screen_width // self.tile_size - 1)
            y = random.randint(0, self.screen_height // self.tile_size - 1)
            if self.map.get_tile_type(x * self.tile_size, y * self.tile_size) == 'grass':
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

                #Melde neue Position zurück an den Server
                x,y = self.player.get_position()
                position_dict = {"x": x, "y": y}
                self.network.send(position_dict)
            
            # Spiellogik: Warte auf eine Eingabe für die Richtung
            if keys[pygame.K_LEFT]:
                self.move_direction = "left"
            elif keys[pygame.K_RIGHT]:
                self.move_direction = "right"
            elif keys[pygame.K_UP]:
                self.move_direction = "up"
            elif keys[pygame.K_DOWN]:
                self.move_direction = "down"

            # Bildschirm aktualisieren
            
            self.screen.fill((255, 255, 255))  # Hintergrundfarbe weiß           
            self.map.draw(self.screen)  # Zeichne die Map
            self.player.draw(self.screen)  # Zeichne die Spielfigur
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()


