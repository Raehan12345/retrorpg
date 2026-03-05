import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.name = name
        
        # core resources
        self.max_health = 100
        self.current_health = 100
        self.max_mana = 50
        self.current_mana = 50
        
        # offensive attributes
        self.attack_damage = 10
        self.magic_damage = 10
        self.crit_chance = 0.05
        self.crit_damage = 1.5
        
        # defensive attributes
        self.armor = 5
        self.cc_resistance = 0.0
        self.dodge_chance = 0.05
        
        # utility attributes
        self.speed = 5
        
        # basic rendering setup
        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def take_damage(self, amount, damage_type="physical"):
        # basic mitigation calculation
        if damage_type == "physical":
            actual_damage = max(1, amount - self.armor)
        else:
            actual_damage = amount
            
        self.current_health -= actual_damage
        
        # prevent health from dropping below zero
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def die(self):
        # remove sprite from all groups
        self.kill()