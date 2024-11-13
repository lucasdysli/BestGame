# main.py
import pygame
import sys
from src.game import Game  
from src.network import Network

# Pygame initialisieren und Spiel starten
pygame.init()
network = Network()
game = Game(network)
game.run()
sys.exit()