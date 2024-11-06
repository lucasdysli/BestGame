# src/tile.py

import pygame
import random

class Tile:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.type = random.choice(["grass", "mountain"])  # Zufälliger Typ: "grass" oder "mountain"
        
        # Lade die Bilddateien für jedes Tile
        self.grass_image = pygame.image.load("assets/images/grass1.png")  # Stelle sicher, dass die Datei existiert
        self.mountain_image = pygame.image.load("assets/images/mountain.png")  # Stelle sicher, dass die Datei existiert
        
        # Skaliere die Bilder auf die Größe des Tiles
        self.grass_image = pygame.transform.scale(self.grass_image, (self.size, self.size))
        self.mountain_image = pygame.transform.scale(self.mountain_image, (self.size, self.size))

    def draw(self, screen):
        # Zeichne das Tile basierend auf dem Typ
        if self.type == "grass":
            screen.blit(self.grass_image, (self.x, self.y))  # Wiesenbild
        elif self.type == "mountain":
            screen.blit(self.mountain_image, (self.x, self.y))  # Gebirgbild

    def get_type(self):
        return self.type  # Gibt den Typ des Tiles zurück (grass oder mountain)

