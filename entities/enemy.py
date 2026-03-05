import pygame
import random
from entities.base_entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, name, enemy_type, level=1):
        # initialize parent class
        super().__init__(x, y, name)
        
        self.enemy_type = enemy_type
        self.level = level
        
        # set enemy color to a distinct red
        self.image.fill((200, 50, 50))
        
        # apply specific stats and scaling based on type
        self.setup_enemy_stats()
        
    def setup_enemy_stats(self):
        # define base stats and scaling for different monsters
        if self.enemy_type == "slime":
            self.max_health = 30 + (self.level * 5)
            self.attack_damage = 5 + (self.level * 2)
            self.speed = 3
            self.exp_reward = 20
        elif self.enemy_type == "goblin":
            self.max_health = 50 + (self.level * 10)
            self.attack_damage = 8 + (self.level * 3)
            self.speed = 5
            self.exp_reward = 45
        elif self.enemy_type == "skeleton":
            self.max_health = 40 + (self.level * 8)
            self.attack_damage = 12 + (self.level * 4)
            self.armor = 5 + (self.level * 2)
            self.speed = 4
            self.exp_reward = 60
        else:
            # default fallback stats
            self.max_health = 20
            self.attack_damage = 5
            self.exp_reward = 10
            
        # heal to full after setting max health
        self.current_health = self.max_health
        
    def map_wander(self, game_map, step_size):
        # give the enemy a small chance to move randomly on the map
        # this is called from the main game loop during exploration
        if random.random() < 0.2:
            direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            next_x = self.rect.x + (direction[0] * step_size)
            next_y = self.rect.y + (direction[1] * step_size)
            
            # check map boundaries and walls before moving
            if game_map.is_walkable(next_x, next_y):
                self.rect.x = next_x
                self.rect.y = next_y