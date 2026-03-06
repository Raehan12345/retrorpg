import pygame
import random
from settings import *

class GameMap:
    def __init__(self):
        self.cols = 20 # Increased map size for better camera testing
        self.rows = 20
        self.tile_size = tile_size
        self.grid = []
        self.generate()

    def generate(self):
        while True:
            self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            for y in range(self.rows):
                for x in range(self.cols):
                    if x == 0 or x == self.cols-1 or y == 0 or y == self.rows-1:
                        self.grid[y][x] = 1
                    elif random.random() < 0.15:
                        self.grid[y][x] = 1
            self.grid[1][1] = 0
            # Flood fill check for connectivity
            floor_count = sum(row.count(0) for row in self.grid)
            visited = set(); queue = [(1, 1)]; visited.add((1, 1))
            while queue:
                cx, cy = queue.pop(0)
                for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < self.cols and 0 <= ny < self.rows:
                        if self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                            visited.add((nx, ny)); queue.append((nx, ny))
            if len(visited) == floor_count: break

    def is_walkable(self, x, y):
        col, row = x // self.tile_size, y // self.tile_size
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.grid[row][col] == 0
        return False

    def get_random_walkable_tile(self):
        while True:
            c, r = random.randint(1, self.cols-2), random.randint(1, self.rows-2)
            if self.grid[r][c] == 0 and (c, r) != (1, 1):
                return c * self.tile_size, r * self.tile_size

    def draw(self, screen, cam_x, cam_y):
        # Only draw tiles visible on screen
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(x * self.tile_size - cam_x, y * self.tile_size - cam_y, self.tile_size, self.tile_size)
                # Optimization: Only blit if visible
                if rect.right > 0 and rect.left < width and rect.bottom > 0 and rect.top < height:
                    if self.grid[y][x] == 1:
                        pygame.draw.rect(screen, (60, 60, 60), rect)
                    else:
                        pygame.draw.rect(screen, (30, 30, 30), rect)
                    pygame.draw.rect(screen, (20, 20, 20), rect, 1)