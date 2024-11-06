import pygame
import os

# Lade das Sprite-Sheet (Bild mit mehreren tides)
sprite_sheet = pygame.image.load("tidesheet.png")

# Definiere die Größe der einzelnen tides
tide_width = 16
tide_height = 16

# Erstelle ein Verzeichnis, in dem die tides gespeichert werden
output_dir = "tides"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Berechne, wie viele tides horizontal und vertikal im Sprite-Sheet sind
sheet_width, sheet_height = sprite_sheet.get_size()
cols = sheet_width // tide_width  # Anzahl der Spalten
rows = sheet_height // tide_height  # Anzahl der Reihen

# Extrahiere jedes tide und speichere es als separate PNG-Datei
tide_count = 0
for row in range(rows):
    for col in range(cols):
        # Bestimme die Position des tides im Sprite-Sheet
        rect = pygame.Rect(col * tide_width, row * tide_height, tide_width, tide_height)
        tide_image = sprite_sheet.subsurface(rect)  # Extrahiere das tide

        # Speichere das tide als einzelne PNG-Datei
        tide_filename = os.path.join(output_dir, f"tide_{tide_count}.png")
        pygame.image.save(tide_image, tide_filename)

        tide_count += 1

print(f"Es wurden {tide_count} tides extrahiert und gespeichert.")
