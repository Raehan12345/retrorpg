import pygame
import random
from entities.base_entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, name, enemy_type, stage=1, is_boss=False):
        super().__init__(x, y, name)
        self.enemy_type = enemy_type
        self.stage = stage
        self.is_boss = is_boss
        
        if self.is_boss:
            self.image = pygame.Surface((80, 80))
            self.image.fill((150, 0, 0))
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            self.image.fill((200, 50, 50))
            
        self.setup_enemy_stats()
        
    def setup_enemy_stats(self):
        scale = 1.0 + (self.stage * 0.15)
        if self.is_boss:
            self.setup_boss_stats(scale)
        else:
            self.setup_regular_stats(scale)
        self.current_health = self.max_health

    def setup_regular_stats(self, scale):
        self.forge_materials = random.randint(0, 1)
        if self.enemy_type == "slime":
            self.max_health = int(30 * scale)
            self.attack_damage = int(5 * scale)
            self.exp_reward = 20 + (self.stage * 5)
            self.gold = random.randint(5, 15) + self.stage
            self.loot_table = [("minor health potion", 40), ("topaz ring", 10), ("frost dagger", 5), (None, 45)]
        elif self.enemy_type == "goblin":
            self.max_health = int(50 * scale)
            self.attack_damage = int(8 * scale)
            self.exp_reward = 40 + (self.stage * 5)
            self.gold = random.randint(15, 30) + self.stage
            self.loot_table = [("iron sword", 10), ("shortbow", 10), ("hunter tunic", 5), ("flame sword", 5), (None, 70)]
        elif self.enemy_type == "skeleton":
            self.max_health = int(40 * scale)
            self.attack_damage = int(12 * scale)
            self.armor = int(5 * scale)
            self.exp_reward = 60 + (self.stage * 5)
            self.gold = random.randint(20, 40) + self.stage
            self.loot_table = [("obsidian dagger", 5), ("venom spear", 5), ("minor mana potion", 40), (None, 50)]
        else:
            self.max_health = int(20 * scale)
            self.attack_damage = int(5 * scale)
            self.exp_reward = 10 + (self.stage * 5)
            self.gold = random.randint(1, 10) + self.stage
            self.loot_table = [(None, 100)]

    def setup_boss_stats(self, scale):
        self.forge_materials = 5 + self.stage
        if self.enemy_type == "dread knight":
            self.max_health = int(120 * scale)
            self.attack_damage = int(15 * scale)
            self.armor = int(8 * scale)
            self.exp_reward = 100 * self.stage
            self.gold = 200 + (self.stage * 50)
            self.loot_table = [("dragon slayer", 30), ("plate armor", 30), ("flame sword", 20), ("mithril mail", 20)]
        elif self.enemy_type == "lich king":
            self.max_health = int(90 * scale)
            self.magic_damage = int(20 * scale)
            self.exp_reward = 120 * self.stage
            self.gold = 250 + (self.stage * 50)
            self.loot_table = [("archmage scepter", 30), ("pendant of life", 30), ("storm bow", 20), ("shadow cloak", 20)]
        else:
            self.max_health = int(100 * scale)
            self.attack_damage = int(15 * scale)
            self.exp_reward = 100 * self.stage
            self.gold = 200 + (self.stage * 50)
            self.loot_table = [(None, 100)]

    def map_wander(self, game_map, step_size):
        if self.is_boss: return 
        if random.random() < 0.1:
            direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            nx = self.rect.x + (direction[0] * step_size)
            ny = self.rect.y + (direction[1] * step_size)
            if game_map.is_walkable(nx, ny):
                self.rect.x = nx
                self.rect.y = ny