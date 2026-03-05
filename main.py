import pygame
from engine.game import Game

if __name__ == "__main__":
    # initialize core modules
    pygame.init()
    
    # boot up the game engine
    game = Game()
    game.run()