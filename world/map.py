import pygame
import random
from settings import *

class GameMap:
    def __init__(self):
        self.cols = width // tile_size
        self.rows = height // tile_size
        self.tile_size = tile_size
        self.grid = []
        self.generate()

    def generate(self):
        while True:
            self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            
            # Randomly place walls
            for y in range(self.rows):
                for x in range(self.cols):
                    if x == 0 or x == self.cols - 1 or y == 0 or y == self.rows - 1:
                        self.grid[y][x] = 1
                    elif random.random() < 0.15:
                        self.grid[y][x] = 1
            
            # Ensure player spawn point is always open
            self.grid[1][1] = 0
            
            # Flood Fill Check for 100% Connectivity
            floor_count = sum(row.count(0) for row in self.grid)
            visited = set()
            queue = [(1, 1)]
            visited.add((1, 1))
            
            while queue:
                cx, cy = queue.pop(0)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.cols and 0 <= ny < self.rows:
                        if self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                            
            # If the number of tiles we could reach equals the total floor tiles, map is valid!
            if len(visited) == floor_count:
                break

    def is_walkable(self, x, y):
        col = x // self.tile_size
        row = y // self.tile_size
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.grid[row][col] == 0
        return False

    def get_random_walkable_tile(self):
        while True:
            col = random.randint(1, self.cols - 2)
            row = random.randint(1, self.rows - 2)
            if self.grid[row][col] == 0 and (col, row) != (1, 1):
                return col * self.tile_size, row * self.tile_size

    def draw(self, screen, camera_x, camera_y):
        # We only loop through tiles that are actually visible to the camera
        start_col = max(0, camera_x // self.tile_size)
        end_col = min(self.cols, (camera_x + width) // self.tile_size + 1)
        start_row = max(0, camera_y // self.tile_size)
        end_row = min(self.rows, (camera_y + height) // self.tile_size + 1)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                # Calculate screen position based on camera
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(screen, (80, 80, 80), rect) # Wall
                else:
                    pygame.draw.rect(screen, (30, 30, 30), rect) # Floor
                pygame.draw.rect(screen, (20, 20, 20), rect, 1) # Grid lines