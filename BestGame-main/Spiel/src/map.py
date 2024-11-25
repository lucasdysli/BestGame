import pygame

class Map:
    def __init__(self, width, height, tile_size, grid):
        self.width = width  # Breite der Map in Feldern
        self.height = height  # Höhe der Map in Feldern
        self.tile_size = tile_size  # Größe der Felder in Pixeln
        
        # 2D-Array für die Map
        self.tiles = grid

        # Wörterbuch für die Bilder der Tiles
        self.tile_images = {}

        # Lade alle möglichen Tile-Bilder dynamisch
        tile_types = ["g", "t", "m1", "m2", "m3", "m4", "m5", "m6", "m7"] 
        for tile_type in tile_types:
            if tile_type == "g":
                image_path = f"C:/Users/admin/Desktop/Tiles/grass_tiles/{tile_type}.png"
            elif tile_type == "t":
                image_path = f"C:/Users/admin/Desktop/Tiles/tree_tiles/{tile_type}.png"
            else:
                image_path = f"C:/Users/admin/Desktop/Tiles/mountain_tiles/{tile_type}.png"
            
            # Lade und skaliere das Bild
            image = pygame.image.load(image_path)
            if tile_type == "t":
                # Skalierung für Bäume (1,5x größer in Breite und Höhe)
                image = pygame.transform.scale(image, (int(self.tile_size * 1.5), int(self.tile_size * 1.5)))
            else:
                # Standard-Skalierung
                image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
            
            self.tile_images[tile_type] = image

    def draw(self, screen):
        # Zeichne jedes Tile auf der Map
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.tiles[row][col]  # Hol das Tile-Objekt an der aktuellen Position
                
                # Berechne die Position des Tiles auf dem Bildschirm
                x = col * self.tile_size
                y = row * self.tile_size

                if tile_type == "t":
                    # Zeichne Grass-Tile als Untergrund
                    if "g" in self.tile_images:
                        screen.blit(self.tile_images["g"], (x, y))
                    
                    # Zeichne Tree-Tile darüber
                    tree_image = self.tile_images["t"]
                    tree_width = tree_image.get_width()
                    tree_height = tree_image.get_height()
                    
                    # Zentriere das Baum-Bild
                    offset_x = (tree_width - self.tile_size) // 2
                    offset_y = tree_height - self.tile_size
                    screen.blit(tree_image, (x - offset_x, y - offset_y))
                elif tile_type in self.tile_images:
                    # Zeichne normale Tiles (keine spezielle Behandlung notwendig)
                    screen.blit(self.tile_images[tile_type], (x, y))

    def get_tile_type(self, x, y):
        # Gibt den Typ des Tiles an den gegebenen Koordinaten (x, y)
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        return self.tiles[tile_y][tile_x]  # Ruft den Typ des Tiles ab
