import pygame

class Map:
    def __init__(self, width, height, tile_size, grid):
        self.width = width  # Breite der Map in Feldern
        self.height = height  # Höhe der Map in Feldern
        self.tile_size = tile_size  # Größe der Felder in Pixeln
        
        # 2D-Array für die Map
        self.tiles = grid

        # Lade die Bilddateien für jedes Tile
        self.grass_image = pygame.image.load("assets/images/grass1.png")  # Stelle sicher, dass die Datei existiert
        self.mountain_image = pygame.image.load("assets/images/mountain.png")  # Stelle sicher, dass die Datei existiert
        
        # Skaliere die Bilder auf die Größe des Tiles
        self.grass_image = pygame.transform.scale(self.grass_image, (self.tile_size, self.tile_size))
        self.mountain_image = pygame.transform.scale(self.mountain_image, (self.tile_size, self.tile_size))


    def draw(self, screen):
        # Zeichne jedes Tile auf der Map
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.tiles[row][col]  # Hol das Tile-Objekt an der aktuellen Position
                
                # Berechne die Position des Tiles auf dem Bildschirm
                x = col * self.tile_size
                y = row * self.tile_size
                
                # Zeichne das entsprechende Bild je nach Tile-Typ
                if tile_type == "g":
                    screen.blit(self.grass_image, (x, y))  # Wiesenbild
                elif tile_type == "m":
                    screen.blit(self.mountain_image, (x, y))  # Gebirgsbild
    
    def get_tile_type(self, x, y):
        # Gibt den Typ des Tiles an den gegebenen Koordinaten (x, y)
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        return self.tiles[tile_y][tile_x]  # Ruft den Typ des Tiles ab



