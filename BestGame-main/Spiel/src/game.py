# src/game.py

import pygame
import time
import random
import socket
import copy
from src.map import Map
from src.player import Player
from src.network import Network

class Game:
    def __init__(self, network):
        
        self.network = network
        self.move_direction = "neutral"  
        self.new_direction = "neutral"
        self.player_positions_dic = {}
        self.last_x_pos = ""
        self.last_y_pos = ""
        self.selected_enemy = None  # Kein Gegner anfangs ausgewählt
        self.last_selected_enemy = None
        self.animation_steps = ["step1", "step2", "step3", "step4", "step5", "step6"]

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

    def select_enemy(self, mouse_pos):
        for player_id, pos in self.network.player_positions_dic.items():
            if player_id == self.network.player_id:
                continue
            player_rect = pygame.Rect(pos["x"] * self.tile_size, pos["y"] * self.tile_size, self.tile_size, self.tile_size)
            if player_rect.collidepoint(mouse_pos):  # Überprüft, ob Klick auf Spieler
                self.selected_enemy = player_id  # Setzt den Spieler als ausgewählt
            else:
                self.selected_enemy = None
                break

    def display_message(self, screen, text, position=(500, 350), font_size=150, color=(0, 0, 0)):
        # Schriftart und Größe festlegen
        font = pygame.font.SysFont(None, font_size)        
        # Text rendern
        text_surface = font.render(text, True, color)        
        # Text auf dem Bildschirm zeichnen
        screen.blit(text_surface, position)


    def run(self):
        running = True
        while running:
            # Event-Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Linke Maustaste
                    mouse_pos = pygame.mouse.get_pos()
                    self.select_enemy(mouse_pos)
                    if self.selected_enemy != self.last_selected_enemy: #Nur bei neuem selected enemy wird an Server gesendet
                        new_enemy = {"type": "enemy_selection", "selected_enemy": self.selected_enemy}
                        self.network.send(new_enemy)
                        self.last_selected_enemy  = copy.deepcopy(self.selected_enemy)

                        # Bildschirm aktualisieren
                        self.screen.fill((255, 255, 255))  # Hintergrundfarbe weiß           
                        self.map.draw(self.screen)  # Zeichne die Map  
                        self.player.draw(self.screen, self.network.player_positions_dic, self.network.player_last_position_dic, self.network.player_id,
                                    self.selected_enemy, self.network.player_life_points_dic, self.move_direction)  # Zeichne die Spielfiguren
                        if self.network.death:
                            self.display_message(self.screen, "Du bist tot!", position=(100, 100), font_size=30, color=(0, 0, 0))
                        pygame.display.flip()
                        self.clock.tick(60)  # 60 FPS


            # Tastenstatus abfragen
            keys = pygame.key.get_pressed()

            #Führe die Bewegung aus, sobald Server sendet
            if self.network.ready_check():
                self.player.move(self.move_direction)  # Führe die Bewegung aus
                self.network.move_done()

                #Melde neue Position zurück an den Server und hole die Positionen der restlichen Spieler
                x, y = self.player.get_position()
                x = x/self.tile_size
                y = y/self.tile_size
                own_position = {"type": "position", "x": x, "y": y}
                if self.network.death:
                    own_position = {"type": "position", "x": 0, "y": 0}
                self.network.send(own_position)
                time.sleep(0.2)

                # Update die eigene Position basierend auf player_id
                if self.network.player_id in self.network.player_positions_dic:
                    position = self.network.player_positions_dic[self.network.player_id]
                    
                    self.player.x = position['x'] * self.tile_size
                    self.player.y = position['y'] * self.tile_size

                # Bildschirm aktualisieren
                self.screen.fill((255, 255, 255))  # Hintergrundfarbe weiß           
                self.map.draw(self.screen)  # Zeichne die Map  
                for step in self.animation_steps:
                    self.player.draw_player_movement(self.screen, self.network.player_positions_dic, self.network.player_last_position_dic, self.network.player_id,
                                    self.selected_enemy, self.network.player_life_points_dic, self.move_direction, animation_step = step)
                    pygame.display.flip()
                    time.sleep(0.1)
                    self.map.draw(self.screen)  # Zeichne die Map  
                self.player.draw(self.screen, self.network.player_positions_dic, self.network.player_last_position_dic, self.network.player_id,
                                    self.selected_enemy, self.network.player_life_points_dic, self.move_direction)  # Zeichne die Spielfiguren
                if self.network.death:
                    self.display_message(self.screen, "Du bist tot!", position=(100, 100), font_size=30, color=(0, 0, 0))
                pygame.display.flip()
            
            # Spiellogik: Warte auf eine Eingabe für die Richtung
            if keys[pygame.K_LEFT]:
                self.new_direction = "left"
            elif keys[pygame.K_RIGHT]:
                self.new_direction = "right"
            elif keys[pygame.K_UP]:
                self.new_direction = "up"
            elif keys[pygame.K_DOWN]:
                self.new_direction = "down"
            elif keys[pygame.K_SPACE]:
                self.new_direction = "neutral"

            if self.new_direction != self.move_direction:  # Überprüfen, ob sich die Richtung geändert hat
                self.move_direction = self.new_direction
                
                # Bildschirm aktualisieren, da eine neue Richtung ausgewählt wurde
                self.screen.fill((255, 255, 255))  # Hintergrundfarbe weiß           
                self.map.draw(self.screen)  # Zeichne die Map  
                self.player.draw(self.screen, self.network.player_positions_dic, self.network.player_last_position_dic, self.network.player_id,
                                    self.selected_enemy, self.network.player_life_points_dic, self.move_direction)  # Zeichne die Spielfiguren
                if self.network.death:
                    self.display_message(self.screen, "Du bist tot!", position=(100, 100), font_size=30, color=(0, 0, 0))
                pygame.display.flip()
                self.clock.tick(60)  # 60 FPS

        self.network.stop()
        pygame.quit()


