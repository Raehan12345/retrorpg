import pygame
from entities.base_entity import Entity
from combat.spells import spell_database
from items.inventory import Inventory
from items.equipment import item_database
from combat.skills import skill_tree_database

class Player(Entity):
    def __init__(self, x, y, name, player_class):
        super().__init__(x, y, name)
        self.player_class = player_class
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
        self.attribute_points = 0
        self.spell_points = 0
        self.passive_points = 0
        self.forge_materials = 0
        
        self.spells = []
        self.unlocked_skills = []
        self.inventory = Inventory()
        
        self.setup_class_stats()
        self.image.fill((50, 200, 50))

    def has_skill(self, effect_type):
        for skill in self.unlocked_skills:
            if skill.effect_type == effect_type:
                return skill.power
        return 0

    def setup_class_stats(self):
        if self.player_class == "warrior":
            self.max_health = 150
            self.attack_damage = 15
            self.armor = 10
            self.spells.append(spell_database["heavy strike"])
            self.inventory.add_item(item_database["iron sword"])
            self.inventory.add_item(item_database["leather tunic"])
            self.inventory.add_item(item_database["minor health potion"])
        elif self.player_class == "mage":
            self.max_health = 80
            self.max_mana = 150
            self.magic_damage = 20
            self.spells.append(spell_database["fireball"])
            self.inventory.add_item(item_database["apprentice staff"])
            self.inventory.add_item(item_database["wizard robe"])
            self.inventory.add_item(item_database["minor mana potion"])
        elif self.player_class == "rogue":
            self.max_health = 100
            self.attack_damage = 12
            self.dodge_chance = 0.15
            self.spells.append(spell_database["shadow step"])
            self.inventory.add_item(item_database["obsidian dagger"])
            self.inventory.add_item(item_database["leather tunic"])
        elif self.player_class == "archer":
            self.max_health = 110
            self.max_mana = 80
            self.attack_damage = 16
            self.armor = 6
            self.speed = 8
            self.spells.append(spell_database["piercing arrow"])
            self.inventory.add_item(item_database["shortbow"])
            self.inventory.add_item(item_database["hunter tunic"])
            self.inventory.add_item(item_database["minor health potion"])
            
        self.current_health = self.max_health
        self.current_mana = self.max_mana

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            return True
        return False

    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        self.attribute_points += 1
        if self.level % 5 == 0:
            self.spell_points += 1
            
        self.current_health = self.max_health
        self.current_mana = self.max_mana