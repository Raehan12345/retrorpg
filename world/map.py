import pygame
from settings import *

class Map:
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
        
        # lock the tile size to 64 pixels for a chunky retro look
        self.tile_size = 64

    def draw(self, surface):
        # iterate through the grid list to draw the appropriate rectangles
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if tile == 1:
                    # draw dark grey wall tile
                    pygame.draw.rect(surface, (80, 80, 80), (x, y, self.tile_size, self.tile_size))
                elif tile == 0:
                    # draw lighter floor tile
                    pygame.draw.rect(surface, (40, 40, 40), (x, y, self.tile_size, self.tile_size))
                    
                # draw a subtle grid outline for that classic tactical rpg feel
                pygame.draw.rect(surface, (20, 20, 20), (x, y, self.tile_size, self.tile_size), 1)

    def is_walkable(self, pixel_x, pixel_y):
        # convert pixel coordinates back to grid indexes
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        
        # prevent indexing errors if the player tries to leave the window
        if grid_y < 0 or grid_y >= len(self.grid) or grid_x < 0 or grid_x >= len(self.grid[0]):
            return False
            
        # check if the target tile is a floor
        return self.grid[grid_y][grid_x] == 0