# src/player.py

import pygame
from src.network import Network


class Player:
    def __init__(self, x, y, tile_size, map_ref):
        self.tile_size = tile_size  # Größe der Felder
        self.x = x  # Startposition x
        self.y = y  # Startposition y
        self.size = 10  # Größe der Spielfigur (optional)
        self.speed = self.tile_size  # Die Geschwindigkeit entspricht der Feldgröße
        self.map = map_ref  # Referenz auf die Map, um Felder zu prüfen
        self.health_bar_width = self.tile_size * 0.7
        self.health_bar_height = 6
        self.health_bar_offset = 25
        self.max_life_points = 100
        self.tile_standing_images = {"blue": {}, "yellow": {}, "red": {}}
        self.tile_movement_images = {"blue": {"right": {}, "left": {}, "up": {}, "down": {}, "neutral": {}}}


        # Lade standing Tiles
        tile_types = ["right", "left", "up", "down", "neutral"]  
        for tile_type in tile_types:
            image_path_blue = f"C:/Users/admin/Desktop/Tiles/warrior_blue/standing/{tile_type}.png"
            image_path_yellow = f"C:/Users/admin/Desktop/Tiles/warrior_yellow/standing/{tile_type}.png"
            image_path_red = f"C:/Users/admin/Desktop/Tiles/warrior_red/standing/{tile_type}.png"
            
            # Lade und skaliere die Bilder
            image_blue = pygame.image.load(image_path_blue)
            image_blue = pygame.transform.scale(image_blue, (int(self.tile_size * 2), int(self.tile_size * 2)))
            image_yellow = pygame.image.load(image_path_yellow)
            image_yellow = pygame.transform.scale(image_yellow, (int(self.tile_size * 2), int(self.tile_size * 2)))
            image_red = pygame.image.load(image_path_red)
            image_red = pygame.transform.scale(image_red, (int(self.tile_size * 2), int(self.tile_size * 2)))
            
            self.tile_standing_images["blue"][tile_type] = image_blue
            self.tile_standing_images["yellow"][tile_type] = image_yellow
            self.tile_standing_images["red"][tile_type] = image_red

        #Lade movement Tiles
        tile_types = ["right", "left", "up", "down", "neutral"]  
        steps = ["step1", "step2", "step3", "step4", "step5", "step6"]
        for tile_type in tile_types:
            for step in steps:
                image_path_blue = f"C:/Users/admin/Desktop/Tiles/warrior_blue/movement/{tile_type}/{step}.png"
                
                # Lade und skaliere die Bilder
                image_blue = pygame.image.load(image_path_blue)
                image_blue = pygame.transform.scale(image_blue, (int(self.tile_size * 2), int(self.tile_size * 2)))

                self.tile_movement_images["blue"][tile_type][step] = image_blue


        #Offset berechnen für Zentrieren aufrgrund von Skalierung
        warrior_image = self.tile_standing_images["blue"]["right"]
        warrior_width = warrior_image.get_width()
        warrior_height = warrior_image.get_height()
        self.offset_x = (warrior_image.get_width() - self.tile_size) // 2
        self.offset_y = warrior_image.get_height() - self.tile_size
   

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
        elif direction == "neutral":
            new_x = self.x
            new_y = self.y

        # Überprüfe, ob das Zielfeld ein Grassfeld ist
        if self.map.get_tile_type(new_x, new_y) == "g":
            # Wenn das Zielfeld ein Grassfeld ist, führe die Bewegung aus
            self.x = new_x
            self.y = new_y

        # Sicherstellen, dass der Spieler innerhalb der Karte bleibt
        self.x = max(0, min(self.x, 800 - self.tile_size))
        self.y = max(0, min(self.y, 600 - self.tile_size))

        # Die Position auf das nächstgelegene Feldzentrum runden
        self.x = round(self.x / self.tile_size) * self.tile_size
        self.y = round(self.y / self.tile_size) * self.tile_size

    def draw(self, screen, player_positions, player_last_positions, own_player_id, selected_enemy, life_points, own_move_direction):

        # Zeichne die Spielfiguren und Lebensbalken
        for player_id, position in player_positions.items():
            player_x = position['x'] * self.tile_size
            player_y = position['y'] * self.tile_size

            if player_id == own_player_id:
                # Zeichne das Spielerbild basierend auf der Richtung
                image_key = own_move_direction
                screen.blit(self.tile_standing_images["blue"][image_key], (player_x - self.offset_x, player_y - self.offset_y))

            elif player_id == selected_enemy:
                move_direction = "neutral"
                if player_id in player_last_positions:
                    move_direction = self.get_move_direction(player_positions[player_id], player_last_positions[player_id])
                image_key = move_direction if move_direction in self.tile_standing_images["red"] else "neutral"
                screen.blit(self.tile_standing_images["red"][image_key], (player_x - self.offset_x, player_y - self.offset_y))

            else:
                move_direction = "neutral"
                if player_id in player_last_positions:
                    move_direction = self.get_move_direction(player_positions[player_id], player_last_positions[player_id])
                image_key = move_direction if move_direction in self.tile_standing_images["yellow"] else "neutral"
                screen.blit(self.tile_standing_images["yellow"][image_key], (player_x - self.offset_x, player_y - self.offset_y))


            self.draw_health_bar(player_id, player_x, player_y, life_points, screen)

    def draw_player_movement(self, screen, player_positions, player_last_positions, own_player_id, selected_enemy, life_points, own_move_direction, animation_step):
        for player_id, position in player_positions.items():
            player_x = position['x'] * self.tile_size
            player_y = position['y'] * self.tile_size


            if player_id == own_player_id:
                move_direction = "neutral"
                if player_id in player_last_positions:
                    move_direction = self.get_move_direction(player_positions[player_id], player_last_positions[player_id])
                image_key = move_direction
                #Offset anpassen mit Berücksichtigung der move direction
                offset_x, offset_y = self.get_offset(image_key, animation_step)
                player_x = player_x - offset_x
                player_y = player_y - offset_y
                screen.blit(self.tile_movement_images["blue"][image_key][animation_step], (player_x, player_y))
                self.draw_health_bar(player_id, player_x + (self.tile_size // 2), player_y + self.tile_size, life_points, screen)

            elif player_id == selected_enemy:
                move_direction = "neutral"
                if player_id in player_last_positions:
                    move_direction = self.get_move_direction(player_positions[player_id], player_last_positions[player_id])
                image_key = move_direction if move_direction in self.tile_standing_images["red"] else "neutral"
                screen.blit(self.tile_standing_images["red"][image_key], (player_x - self.offset_x, player_y - self.offset_y))
                self.draw_health_bar(player_id, player_x, player_y, life_points, screen)

            else:
                move_direction = "neutral"
                if player_id in player_last_positions:
                    move_direction = self.get_move_direction(player_positions[player_id], player_last_positions[player_id])
                image_key = move_direction if move_direction in self.tile_standing_images["yellow"] else "neutral"
                screen.blit(self.tile_standing_images["yellow"][image_key], (player_x - self.offset_x, player_y - self.offset_y))
                self.draw_health_bar(player_id, player_x, player_y, life_points, screen)
            
    

    def get_move_direction(self, position, last_position):
        x_pos = position["x"]
        y_pos = position["y"]
        x_last_pos = last_position["x"]
        y_last_pos = last_position["y"]

        if int(x_pos - x_last_pos) == 1:
            move_direction = "right"
        elif int(x_pos - x_last_pos) == -1:
            move_direction = "left"
        elif int(y_pos - y_last_pos) == 1:
            move_direction = "down"    
        elif int(y_pos - y_last_pos) == -1:
            move_direction = "up"     
        else:
            move_direction = "neutral"     

        return move_direction    
                
    def draw_health_bar(self, player_id, player_x, player_y, life_points, screen):
        # Berechne die Lebensbalkenbreite basierend auf den Lebenspunkten
        current_life = life_points.get(player_id, 0)
        green_bar_width = max(0, int((current_life / self.max_life_points) * self.health_bar_width))
        # Zeichne den grauen Hintergrund des Balkens (volle Länge)
        pygame.draw.rect(screen, (100, 100, 100), 
                        (player_x + self.tile_size // 2 - self.health_bar_width // 2, 
                        player_y - self.health_bar_offset, self.health_bar_width, self.health_bar_height))
        # Zeichne den grünen Vordergrund des Balkens (verbleibende Gesundheit)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (player_x + self.tile_size // 2 - self.health_bar_width // 2, 
                        player_y - self.health_bar_offset, green_bar_width, self.health_bar_height))

    def get_offset(self, move_direction, animation_step):
        # Transformiere animation_step zu Integer
        step_number = int(animation_step.lstrip("step"))  # Entfernt "step" und konvertiert den Rest in einen Integer
        fraction = step_number / 7  # Verwende Fließkomma-Division
        
        if move_direction == "right":
            offset_x = self.offset_x + (self.tile_size * (1 - fraction))
            offset_y = self.offset_y
        elif move_direction == "left":
            offset_x = self.offset_x - (self.tile_size * (1 - fraction))
            offset_y = self.offset_y
        elif move_direction == "up":
            offset_y = self.offset_y - (self.tile_size * (1 - fraction))
            offset_x = self.offset_x
        elif move_direction == "down":
            offset_y = self.offset_y + (self.tile_size * (1 - fraction))
            offset_x = self.offset_x
        else:
            offset_x = self.offset_x
            offset_y = self.offset_y

        return offset_x, offset_y



    def get_position(self):
        return self.x, self.y
