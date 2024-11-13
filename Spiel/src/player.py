# src/player.py

import pygame
from src.network import Network

class Player:
    def __init__(self, x, y, tile_size, map_ref):
        self.tile_size = tile_size  # Größe der Felder
        self.x = x  # Startposition x
        self.y = y  # Startposition y
        self.own_color = (0, 128, 255)  # Blau
        self.other_color = (255, 0, 0)  # Rot
        self.size = 10  # Größe der Spielfigur (optional)
        self.speed = self.tile_size  # Die Geschwindigkeit entspricht der Feldgröße
        self.map = map_ref  # Referenz auf die Map, um Felder zu prüfen

    def move(self, direction):
        # Berechne die neue Position basierend auf der Richtung
        new_x = self.x
        new_y = self.y

        if direction == "left":
            new_x -= self.speed
        elif direction == "right":
            new_x += self.speed
        elif direction == "up":
            new_y -= self.speed
        elif direction == "down":
            new_y += self.speed

        # Überprüfe, ob das Zielfeld ein Gebirgsfeld ist
        if self.map.get_tile_type(new_x, new_y) != "m":
            # Wenn das Zielfeld kein Gebirgsfeld ist, führe die Bewegung aus
            self.x = new_x
            self.y = new_y

        # Sicherstellen, dass der Spieler innerhalb der Karte bleibt
        self.x = max(0, min(self.x, 800 - self.tile_size))
        self.y = max(0, min(self.y, 600 - self.tile_size))

        # Die Position auf das nächstgelegene Feldzentrum runden
        self.x = round(self.x / self.tile_size) * self.tile_size
        self.y = round(self.y / self.tile_size) * self.tile_size

    def draw(self, screen, player_positions):
        # Zeichne die Spielfigur des eigenen Spielers
        pygame.draw.circle(screen, self.own_color, (self.x + self.tile_size // 2, self.y + self.tile_size // 2), self.size)
        
        # Zeichne die Spielfiguren der anderen Spieler
        for player_id, position in player_positions.items():
            # hole die x- und y-Koordinaten des aktuellen Spielers
            player_x = position['x']
            player_y = position['y']
            pygame.draw.circle(screen, self.other_color, (player_x + self.tile_size // 2, player_y + self.tile_size // 2), self.size)

    def get_position(self):
        return self.x, self.y
