import pygame
from entities.base_entity import Entity
from combat.spells import spell_database
from items.inventory import Inventory
from items.equipment import item_database
from combat.skills import skill_tree_database
from utils.assets import AssetManager
from settings import *

class Player(Entity):
    def __init__(self, x, y, name, player_class):
        super().__init__(x, y, name)
        self.player_class = player_class
        self.level = 1; self.experience = 0; self.exp_to_next_level = 100
        self.attribute_points = 0; self.spell_points = 0; self.passive_points = 0; self.forge_materials = 0
        self.spells = []; self.unlocked_skills = []; self.inventory = Inventory()
        self.setup_class_stats()
        
        # Animation State
        self.frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()
        self.animation_speed = 200 
        
        # Surface for layered rendering (Admurin style)
        self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.update_sprite()

    # RESTORED: Vital for combat passive calculations
    def has_skill(self, effect_type):
        for skill in self.unlocked_skills:
            if skill.effect_type == effect_type: 
                return skill.power
        return 0

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.animation_speed:
            self.last_anim_time = now
            # Idle animations in this pack are 4 frames
            self.frame_index = (self.frame_index + 1) % 4
            self.update_sprite()

    def update_sprite(self):
        self.image.fill((0, 0, 0, 0))
        # Loading 128x128 frames, scaled to 64x64
        base = AssetManager.load_sprite_sheet("Base", "Idle_Character.png")
        if base: self.image.blit(base[self.frame_index % len(base)], (0, 0))
            
        weapon = self.inventory.equipped.get("weapon")
        if weapon:
            w_name = getattr(weapon, "original_name", weapon.name).lower()
            folder = "Sword"; fname = "B_Idle_1H_Sword_Retro.png"
            if "bow" in w_name: folder, fname = "Bows", "B_Idle_Bow_Retro.png"
            elif "staff" in w_name or "wand" in w_name: folder, fname = "Staff", "B_Idle_Staff_Retro.png"
            
            w_frames = AssetManager.load_sprite_sheet(folder, fname, is_layer=True)
            if w_frames: self.image.blit(w_frames[self.frame_index % len(w_frames)], (0, 0))

    def draw_inventory_preview(self, screen, x, y):
        # Reduced size to 120x120 for a more compact UI
        box_size = 120
        # Character is scaled to 100 to fit comfortably with padding
        preview = pygame.transform.scale(self.image, (100, 100))
        
        # Draw the background and border
        pygame.draw.rect(screen, (30, 30, 30), (x, y, box_size, box_size))
        pygame.draw.rect(screen, gold, (x, y, box_size, box_size), 2)
        
        # Perfect Centering: (120 box - 100 player) / 2 = 10px padding
        screen.blit(preview, (x + 10, y + 10))

    def setup_class_stats(self):
        if self.player_class == "warrior":
            self.max_health = 150; self.attack_damage = 15; self.armor = 10
            self.spells.append(spell_database["heavy strike"])
            self.inventory.add_item(item_database["iron sword"])
        elif self.player_class == "mage":
            self.max_health = 80; self.max_mana = 150; self.magic_damage = 20
            self.spells.append(spell_database["fireball"])
            self.inventory.add_item(item_database["apprentice staff"])
        elif self.player_class == "rogue":
            self.max_health = 100; self.attack_damage = 12; self.dodge_chance = 0.15
            self.spells.append(spell_database["shadow step"])
            self.inventory.add_item(item_database["iron sword"]) 
        elif self.player_class == "archer":
            self.max_health = 110; self.max_mana = 80; self.attack_damage = 16
            self.armor = 6; self.speed = 8
            self.spells.append(spell_database["piercing arrow"])
            self.inventory.add_item(item_database["shortbow"])
        self.current_health, self.current_mana = self.max_health, self.max_mana

    def gain_experience(self, amount):
        self.experience += amount
        return self.experience >= self.exp_to_next_level

    def level_up(self):
        self.level += 1; self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.attribute_points += 1
        if self.level % 5 == 0: self.spell_points += 1
        self.current_health, self.current_mana = self.max_health, self.max_mana