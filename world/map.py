import pygame
import random
from settings import *

class GameMap:
    def __init__(self):
        # 0 is walkable floor, 1 is a solid wall
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        # tile size matches the asset resolution
        self.tile_size = 64

    def draw(self, surface):
        # iterate through the grid to render tiles
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if tile == 1:
                    # wall color
                    pygame.draw.rect(surface, (80, 80, 80), (x, y, self.tile_size, self.tile_size))
                elif tile == 0:
                    # floor color
                    pygame.draw.rect(surface, (40, 40, 40), (x, y, self.tile_size, self.tile_size))
                    
                # grid lines for retro aesthetic
                pygame.draw.rect(surface, (20, 20, 20), (x, y, self.tile_size, self.tile_size), 1)

    def is_walkable(self, pixel_x, pixel_y):
        # convert pixels to grid index
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        
        # bounds check
        if grid_y < 0 or grid_y >= len(self.grid) or grid_x < 0 or grid_x >= len(self.grid[0]):
            return False
            
        return self.grid[grid_y][grid_x] == 0

    def get_random_walkable_tile(self):
        # find all tiles that are not walls
        walkable_tiles = []
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                if tile == 0:
                    walkable_tiles.append((col_index * self.tile_size, row_index * self.tile_size))
        
        if walkable_tiles:
            return random.choice(walkable_tiles)
        return (self.tile_size, self.tile_size) # fallback to top left