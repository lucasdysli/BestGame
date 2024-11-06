# src/map.py
import pygame
from src.tile import Tile

class Map:
    def __init__(self, width, height, tile_size):
        self.width = width  # Breite der Map in Feldern
        self.height = height  # Höhe der Map in Feldern
        self.tile_size = tile_size  # Größe der Felder in Pixeln
        
        # 2D-Array für die Map
        self.tiles = []
        
        # Fülle die Map mit Tiles
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Tile(x * self.tile_size, y * self.tile_size, self.tile_size))
            self.tiles.append(row)

    def draw(self, screen):
        # Zeichne jedes Tile auf der Map
        for row in self.tiles:
            for tile in row:
                tile.draw(screen)
    
    def get_tile_type(self, x, y):
        # Gibt den Typ des Tiles an den gegebenen Koordinaten (x, y)
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        return self.tiles[tile_y][tile_x].get_type()  # Ruft den Typ des Tiles ab


