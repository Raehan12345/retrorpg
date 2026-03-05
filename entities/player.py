import pygame
from entities.base_entity import Entity
from combat.spells import spell_database
from items.inventory import Inventory
from items.equipment import item_database

class Player(Entity):
    def __init__(self, x, y, name, player_class):
        # call the parent class initialization
        super().__init__(x, y, name)
        
        self.player_class = player_class
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
        # list to hold learned spells
        self.spells = []
        
        # initialize the player inventory
        self.inventory = Inventory()
        
        # apply base stats based on chosen class archetype
        self.setup_class_stats()
        
        # set player specific color to green to differentiate from enemies
        self.image.fill((50, 200, 50))
        
    def setup_class_stats(self):
        # define base stats and growth rates for different classes
        if self.player_class == "warrior":
            self.max_health = 150
            self.attack_damage = 15
            self.armor = 10
            self.speed = 4
            self.health_growth = 20
            self.attack_growth = 3
            
            # assign warrior abilities
            self.spells.append(spell_database["heavy strike"])
            self.spells.append(spell_database["shield bash"])
            
            # assign starting warrior gear
            self.inventory.add_item(item_database["iron sword"])
            self.inventory.add_item(item_database["leather tunic"])
            self.inventory.add_item(item_database["minor health potion"])
            
        elif self.player_class == "mage":
            self.max_health = 80
            self.max_mana = 150
            self.magic_damage = 20
            self.armor = 2
            self.speed = 5
            self.health_growth = 10
            self.magic_growth = 5
            
            # assign mage abilities
            self.spells.append(spell_database["fireball"])
            self.spells.append(spell_database["ice shard"])
            
            # assign starting mage gear
            self.inventory.add_item(item_database["apprentice staff"])
            self.inventory.add_item(item_database["wizard robe"])
            self.inventory.add_item(item_database["minor mana potion"])
            
        elif self.player_class == "rogue":
            self.max_health = 100
            self.attack_damage = 12
            self.crit_chance = 0.15
            self.dodge_chance = 0.15
            self.speed = 7
            self.health_growth = 15
            self.attack_growth = 2
            self.speed_growth = 1
            
            # assign rogue abilities
            self.spells.append(spell_database["poison blade"])
            self.spells.append(spell_database["shadow step"])
            
            # assign starting rogue gear
            self.inventory.add_item(item_database["obsidian dagger"])
            self.inventory.add_item(item_database["leather tunic"])
            
        else:
            # default fallback stats
            self.health_growth = 10
            self.attack_growth = 2
            
        # heal to full after setting max health
        self.current_health = self.max_health
        self.current_mana = self.max_mana

    def gain_experience(self, amount):
        # add experience and check for level up
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        
        # carry over excess experience
        self.experience -= self.exp_to_next_level
        
        # increase required exp for next level by 50 percent
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # apply baseline stat growth
        self.max_health += self.health_growth
        
        # apply class specific stat growth
        if self.player_class == "warrior":
            self.attack_damage += self.attack_growth
            self.armor += 2
        elif self.player_class == "mage":
            self.magic_damage += self.magic_growth
            self.max_mana += 20
        elif self.player_class == "rogue":
            self.attack_damage += self.attack_growth
            self.speed += getattr(self, "speed_growth", 0)
            
        # restore health and mana on level up
        self.current_health = self.max_health
        self.current_mana = self.max_mana
        
        print(f"{self.name} reached level {self.level}!")