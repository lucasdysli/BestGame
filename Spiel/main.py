# main.py
import pygame
import sys
from src.game import Game  # Importiere die Game-Klasse

# Pygame initialisieren und Spiel starten
pygame.init()
game = Game()
game.run()
sys.exit()