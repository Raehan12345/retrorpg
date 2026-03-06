import pygame
import sys
import random
import copy
import json
import os
from settings import *
from world.map import GameMap
from world.objects import Chest, ExitPortal, Forge
from entities.player import Player
from entities.enemy import Enemy
from combat.battle_system import BattleSystem
from combat.skills import skill_tree_database
from combat.spells import class_spell_pools, spell_database
from items.equipment import item_database
from utils.assets import AssetManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("retro rpg")
        self.clock = pygame.time.Clock()
        
        self.font_main = pygame.font.Font(None, 74)
        self.font_sub = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 22)
        self.running = True
        self.state = state_main_menu
        
        self.menu_options = ["start game", "continue", "settings"]
        self.menu_selection = 0
        self.menu_message = ""
        self.temp_name = ""
        self.class_options = ["warrior", "mage", "rogue", "archer"]
        self.class_selection = 0
        self.current_stage = 1
        
        self.shop_items = []
        self.shop_selection = 0
        self.shop_tab = "buy"
        self.shop_sell_scroll = 0
        self.shop_confirm_sell = None 
        self.messages = []
        
        self.inv_tab = "equipped"
        self.inv_selection = 0
        self.inv_bag_scroll = 0
        
        self.forge_selection = 0
        self.forge_scroll = 0
        
        self.enemies = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.forges = pygame.sprite.Group()
        self.exits = pygame.sprite.Group()
        
        self.level_up_tab = "stats"
        self.level_up_options = ["max_health", "max_mana", "attack_damage", "magic_damage", "armor", "speed"]
        self.skill_options = list(skill_tree_database.keys())
        self.level_up_selection = 0
        
        self.player = None
        self.game_map = None
        self.battle_system = None
        self.save_file = "savegame.json"
        
        self.last_x = 64
        self.last_y = 64

    def add_message(self, text):
        self.messages.append(text)
        if len(self.messages) > 5: self.messages.pop(0)

    def save_game(self):
        if not self.player: return
        save_data = {
            "player": {
                "name": self.player.name,
                "class": self.player.player_class,
                "level": self.player.level,
                "exp": self.player.experience,
                "exp_next": self.player.exp_to_next_level,
                "attribute_points": self.player.attribute_points,
                "spell_points": self.player.spell_points,
                "passive_points": self.player.passive_points,
                "hp": self.player.current_health,
                "max_hp": self.player.max_health,
                "mp": self.player.current_mana,
                "max_mp": self.player.max_mana,
                "attack": self.player.attack_damage,
                "magic": self.player.magic_damage,
                "armor": self.player.armor,
                "speed": self.player.speed,
                "gold": self.player.gold,
                "forge_materials": getattr(self.player, "forge_materials", 0),
                "skills": [s.name for s in self.player.unlocked_skills],
                "spells": [{"name": s.name, "level": s.level} for s in self.player.spells],
                "bag": [{"name": i.original_name, "quantity": getattr(i, 'quantity', 1), "upgrade": getattr(i, 'upgrade_level', 0)} for i in self.player.inventory.bag],
                "equipped": {k: ({"name": v.original_name, "upgrade": getattr(v, 'upgrade_level', 0)} if v else None) for k, v in self.player.inventory.equipped.items()}
            },
            "stage": self.current_stage
        }
        with open(self.save_file, "w") as f:
            json.dump(save_data, f)
        self.add_message("game saved successfully.")

    def load_game(self):
        if not os.path.exists(self.save_file):
            self.menu_message = "no save file found!"
            return False
        with open(self.save_file, "r") as f:
            data = json.load(f)
        p_data = data["player"]
        self.init_game_world(p_data["name"], p_data["class"])
        self.current_stage = data["stage"]
        self.player.level = p_data["level"]; self.player.experience = p_data["exp"]
        self.player.exp_to_next_level = p_data["exp_next"]
        self.player.attribute_points = p_data.get("attribute_points", 0)
        self.player.spell_points = p_data.get("spell_points", 0)
        self.player.passive_points = p_data.get("passive_points", 0)
        self.player.max_health = p_data["max_hp"]; self.player.current_health = p_data["hp"]
        self.player.max_mana = p_data["max_mp"]; self.player.current_mana = p_data["mp"]
        self.player.attack_damage = p_data["attack"]; self.player.magic_damage = p_data["magic"]
        self.player.armor = p_data["armor"]; self.player.speed = p_data["speed"]
        self.player.gold = p_data["gold"]; self.player.forge_materials = p_data.get("forge_materials", 0)
        self.player.unlocked_skills = [skill_tree_database[s] for s in p_data["skills"]]
        self.player.spells = []
        for sp in p_data["spells"]:
            spell_obj = copy.deepcopy(spell_database[sp["name"]])
            spell_obj.level = sp["level"]
            self.player.spells.append(spell_obj)
        self.player.inventory.bag = []
        for b_item in p_data["bag"]:
            new_item = copy.deepcopy(item_database[b_item["name"]])
            new_item.quantity = b_item.get("quantity", 1)
            upgrades = b_item.get("upgrade", 0)
            if hasattr(new_item, "upgrade"):
                for _ in range(upgrades): new_item.upgrade()
            self.player.inventory.bag.append(new_item)
        for slot, item_data in p_data["equipped"].items():
            if item_data:
                new_item = copy.deepcopy(item_database[item_data["name"]])
                upgrades = item_data.get("upgrade", 0)
                if hasattr(new_item, "upgrade"):
                    for _ in range(upgrades): new_item.upgrade()
                self.player.inventory.equipped[slot] = new_item
            else: self.player.inventory.equipped[slot] = None
        self.generate_stage()
        self.state = state_exploration
        return True

    def init_game_world(self, name, p_class):
        self.game_map = GameMap()
        self.player = Player(64, 64, name, p_class)
        self.last_x, self.last_y = 64, 64
        self.battle_system = BattleSystem(self.screen)
        self.generate_stage()
        self.state = state_exploration

    def generate_stage(self):
        self.enemies.empty(); self.chests.empty(); self.forges.empty(); self.exits.empty()
        if random.random() < 0.25:
            fx, fy = self.game_map.get_random_walkable_tile()
            self.forges.add(Forge(fx, fy))
        if self.current_stage % 5 == 0:
            x, y = self.game_map.get_random_walkable_tile()
            b_type = random.choice(["dread knight", "lich king"])
            self.enemies.add(Enemy(x, y, b_type.upper(), b_type, self.current_stage, True))
            self.add_message(f"boss floor! defeat {b_type.upper()} to proceed.")
        else:
            num_enemies = 2 + (self.current_stage // 2)
            for _ in range(num_enemies):
                x, y = self.game_map.get_random_walkable_tile()
                e_type = random.choice(["slime", "goblin", "skeleton"])
                self.enemies.add(Enemy(x, y, f"enemy_{_}", e_type, self.current_stage))
            cx, cy = self.game_map.get_random_walkable_tile()
            self.chests.add(Chest(cx, cy, self.current_stage))
            self.add_message(f"entered stage {self.current_stage}.")
        ex, ey = self.game_map.get_random_walkable_tile()
        self.exits.add(ExitPortal(ex, ey))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == state_main_menu: self.handle_menu_input(event.key)
                elif self.state == state_naming: self.handle_naming_input(event)
                elif self.state == state_class_select: self.handle_class_input(event.key)
                elif self.state == state_exploration: self.handle_exploration_input(event.key)
                elif self.state == state_combat: self.handle_combat_input(event.key)
                elif self.state == state_inventory: self.handle_inventory_input(event.key)
                elif self.state == state_level_up: self.handle_level_up_input(event.key)
                elif self.state == state_shop: self.handle_shop_input(event.key)
                elif self.state == "forge": self.handle_forge_input(event.key)
                elif self.state == state_info:
                    if event.key in [pygame.K_c, pygame.K_ESCAPE]: self.state = state_exploration

    def handle_menu_input(self, key):
        self.menu_message = ""
        if key in [pygame.K_UP, pygame.K_w]: self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
        elif key in [pygame.K_DOWN, pygame.K_s]: self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            if self.menu_selection == 0: self.state = state_naming
            elif self.menu_selection == 1: self.load_game()

    def handle_naming_input(self, event):
        if event.key == pygame.K_RETURN and len(self.temp_name) > 0: self.state = state_class_select
        elif event.key == pygame.K_BACKSPACE: self.temp_name = self.temp_name[:-1]
        elif len(self.temp_name) < 12 and event.unicode.isalnum(): self.temp_name += event.unicode

    def handle_class_input(self, key):
        if key in [pygame.K_UP, pygame.K_w]: self.class_selection = (self.class_selection - 1) % len(self.class_options)
        elif key in [pygame.K_DOWN, pygame.K_s]: self.class_selection = (self.class_selection + 1) % len(self.class_options)
        elif key == pygame.K_RETURN: self.init_game_world(self.temp_name, self.class_options[self.class_selection])

    def handle_exploration_input(self, key):
        nx, ny = self.player.rect.x, self.player.rect.y
        step = 64
        if key in [pygame.K_LEFT, pygame.K_a]: nx -= step
        elif key in [pygame.K_RIGHT, pygame.K_d]: nx += step
        elif key in [pygame.K_UP, pygame.K_w]: ny -= step
        elif key in [pygame.K_DOWN, pygame.K_s]: ny += step
        elif key == pygame.K_i: self.state = state_inventory
        elif key == pygame.K_c: self.state = state_info
        elif key == pygame.K_F5: self.save_game()
        elif key == pygame.K_l:
            if self.player.attribute_points > 0 or self.player.spell_points > 0 or self.player.passive_points > 0:
                self.state = state_level_up
            else: self.add_message("no unspent points available.")
        if self.game_map.is_walkable(nx, ny):
            self.last_x, self.last_y = self.player.rect.x, self.player.rect.y
            self.player.rect.x, self.player.rect.y = nx, ny
            self.check_collisions()

    def handle_inventory_input(self, key):
        if key in [pygame.K_i, pygame.K_ESCAPE]:
            self.state = state_exploration; return
        if key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]:
            self.inv_tab = "bag" if self.inv_tab == "equipped" else "equipped"
            self.inv_selection = 0; self.inv_bag_scroll = 0
            
        eq_list = list(self.player.inventory.equipped.keys())
        limit = len(eq_list) if self.inv_tab == "equipped" else len(self.player.inventory.bag)
        
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.inv_selection = (self.inv_selection - 1) % limit
                if self.inv_tab == "bag" and self.inv_selection < self.inv_bag_scroll: self.inv_bag_scroll = self.inv_selection
                elif self.inv_tab == "bag" and self.inv_selection >= self.inv_bag_scroll + 7: self.inv_bag_scroll = max(0, self.inv_selection - 6)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.inv_selection = (self.inv_selection + 1) % limit
                if self.inv_tab == "bag" and self.inv_selection >= self.inv_bag_scroll + 7: self.inv_bag_scroll = self.inv_selection - 6
                elif self.inv_tab == "bag" and self.inv_selection < self.inv_bag_scroll: self.inv_bag_scroll = self.inv_selection
            elif key == pygame.K_RETURN:
                if self.inv_tab == "equipped":
                    slot = eq_list[self.inv_selection]
                    if self.player.inventory.equipped[slot]:
                        self.player.inventory.unequip(slot, self.player)
                        self.add_message(f"unequipped {slot}.")
                elif self.inv_tab == "bag":
                    item = self.player.inventory.bag[self.inv_selection]
                    if item.item_type == "equipment":
                        self.player.inventory.equip(item, self.player)
                        self.add_message(f"equipped {item.original_name}.")
                    elif item.item_type == "consumable":
                        success, msg = item.use(self.player)
                        if success:
                            self.player.inventory.remove_item(item); self.add_message(msg)
            elif key == pygame.K_x:
                if self.inv_tab == "bag":
                    item = self.player.inventory.bag[self.inv_selection]
                    if item.item_type == "equipment":
                        mats = {"common": 1, "uncommon": 2, "rare": 4, "epic": 8, "legendary": 15}.get(item.rarity, 1)
                        mats += (item.upgrade_level * 2); self.player.forge_materials += mats
                        self.player.inventory.remove_item(item); self.add_message(f"dismantled {item.name} for {mats} shards.")
                        
        if key == pygame.K_SPACE:
            self.player.inventory.auto_equip(self.player); self.add_message("optimized gear auto-equipped.")
        
        # CLAMP FIX: Ensures cursor doesn't crash game when items are moved or destroyed
        limit = len(eq_list) if self.inv_tab == "equipped" else len(self.player.inventory.bag)
        if limit == 0: self.inv_selection = 0
        elif self.inv_selection >= limit: self.inv_selection = limit - 1

    def handle_level_up_input(self, key):
        if key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]: self.state = state_exploration; return
        if key == pygame.K_TAB:
            tabs = ["stats", "skills", "spells"]
            curr_idx = tabs.index(self.level_up_tab)
            self.level_up_tab = tabs[(curr_idx + 1) % 3]
            self.level_up_selection = 0; return
        pool = class_spell_pools[self.player.player_class]
        limit = len(self.level_up_options) if self.level_up_tab == "stats" else (len(self.skill_options) if self.level_up_tab == "skills" else len(pool))
        if key in [pygame.K_UP, pygame.K_w]: self.level_up_selection = (self.level_up_selection - 1) % limit
        elif key in [pygame.K_DOWN, pygame.K_s]: self.level_up_selection = (self.level_up_selection + 1) % limit
        elif key == pygame.K_RETURN:
            if self.level_up_tab == "stats" and self.player.attribute_points >= 1:
                stat = self.level_up_options[self.level_up_selection]
                if stat in ["max_health", "max_mana"]: setattr(self.player, stat, getattr(self.player, stat) + 20)
                else: setattr(self.player, stat, getattr(self.player, stat) + 2)
                self.player.attribute_points -= 1
            elif self.level_up_tab == "skills":
                skill = skill_tree_database[self.skill_options[self.level_up_selection]]
                if skill not in self.player.unlocked_skills and self.player.passive_points >= skill.cost:
                    self.player.passive_points -= skill.cost; self.player.unlocked_skills.append(skill)
                    self.add_message(f"trait unlocked: {skill.name.upper()}")
            elif self.level_up_tab == "spells" and self.player.spell_points >= 1:
                spell_name = pool[self.level_up_selection]
                learned = next((s for s in self.player.spells if s.name == spell_name), None)
                if learned and learned.level < learned.max_level:
                    learned.level += 1; self.player.spell_points -= 1; self.add_message(f"upgraded {spell_name} to lvl {learned.level}.")
                elif not learned and len(self.player.spells) < 4:
                    self.player.spells.append(copy.deepcopy(spell_database[spell_name])); self.player.spell_points -= 1; self.add_message(f"learned {spell_name}.")

    def generate_shop_items(self):
        items = ["major health potion", "major mana potion"]
        pools = {"warrior": ["broadsword", "steel claymore", "flame sword", "dragon slayer", "chainmail", "plate armor", "obsidian band"],
                 "mage": ["sage wand", "archmage scepter", "wizard robe", "elder cloak", "topaz ring", "sapphire necklace"],
                 "rogue": ["obsidian dagger", "frost dagger", "shadow fang", "leather tunic", "shadow cloak", "emerald band"],
                 "archer": ["longbow", "venom spear", "storm bow", "hunter tunic", "emerald band", "ruby ring"]}
        pool = pools.get(self.player.player_class, [])
        if pool: items.extend(random.sample(pool, min(3, len(pool))))
        return items

    def handle_shop_input(self, key):
        if self.shop_confirm_sell:
            if key == pygame.K_y:
                item = self.shop_confirm_sell["item"]; slot = self.shop_confirm_sell["slot"]
                val = 20 * self.current_stage; self.player.inventory.unequip(slot, self.player)
                self.player.inventory.remove_item(item); self.player.gold += val
                self.add_message(f"sold equipped {item.name} for {val}g."); self.shop_confirm_sell = None
            elif key in [pygame.K_n, pygame.K_ESCAPE]: self.shop_confirm_sell = None
            return
        if key in [pygame.K_ESCAPE, pygame.K_SPACE]: self.state = state_exploration; return
        if key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]:
            self.shop_tab = "sell" if self.shop_tab == "buy" else "buy"
            self.shop_selection = 0; self.shop_sell_scroll = 0; return
        sellables = [{"source": "equipped", "slot": k, "item": v} for k,v in self.player.inventory.equipped.items() if v] + [{"source": "bag", "index": i, "item": v} for i,v in enumerate(self.player.inventory.bag)]
        limit = len(self.shop_items) if self.shop_tab == "buy" else len(sellables)
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.shop_selection = (self.shop_selection - 1) % limit
                if self.shop_tab == "sell" and self.shop_selection < self.shop_sell_scroll: self.shop_sell_scroll = self.shop_selection
                elif self.shop_tab == "sell" and self.shop_selection >= self.shop_sell_scroll + 7: self.shop_sell_scroll = max(0, self.shop_selection - 6)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.shop_selection = (self.shop_selection + 1) % limit
                if self.shop_tab == "sell" and self.shop_selection >= self.shop_sell_scroll + 7: self.shop_sell_scroll = self.shop_selection - 6
                elif self.shop_tab == "sell" and self.shop_selection < self.shop_sell_scroll: self.shop_sell_scroll = self.shop_selection
            elif key == pygame.K_RETURN:
                if self.shop_tab == "buy":
                    ikey = self.shop_items[self.shop_selection]; cost = 50 * self.current_stage
                    if self.player.gold >= cost:
                        self.player.gold -= cost; self.player.inventory.add_item(item_database[ikey])
                        self.add_message(f"purchased {item_database[ikey].name}.")
                elif self.shop_tab == "sell":
                    sell_info = sellables[self.shop_selection]
                    if sell_info["source"] == "equipped": self.shop_confirm_sell = sell_info
                    else:
                        item = sell_info["item"]; val = 20 * self.current_stage
                        self.player.gold += val; self.player.inventory.remove_item(item)
                        self.add_message(f"sold {item.name} for {val}g.")
                        limit = len([v for v in self.player.inventory.equipped.values() if v]) + len(self.player.inventory.bag)
                        if limit == 0: self.shop_selection = 0
                        elif self.shop_selection >= limit: self.shop_selection = limit - 1

    def handle_forge_input(self, key):
        if key in [pygame.K_ESCAPE, pygame.K_SPACE]:
            self.state = state_exploration; self.player.rect.x = getattr(self, "last_x", self.player.rect.x); return
        forgeables = [i for i in self.player.inventory.bag if i.item_type == "equipment"]
        limit = len(forgeables)
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.forge_selection = (self.forge_selection - 1) % limit
                if self.forge_selection < self.forge_scroll: self.forge_scroll = self.forge_selection
                elif self.forge_selection >= self.forge_scroll + 10: self.forge_scroll = max(0, self.forge_selection - 9)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.forge_selection = (self.forge_selection + 1) % limit
                if self.forge_selection >= self.forge_scroll + 10: self.forge_scroll = self.forge_selection - 9
            elif key == pygame.K_RETURN:
                item = forgeables[self.forge_selection]; cost = 1 + (item.upgrade_level * 2)
                chance = max(0.1, 1.0 - (item.upgrade_level * 0.08))
                if item.upgrade_level >= 10: self.add_message("max level reached!")
                elif self.player.forge_materials >= cost:
                    self.player.forge_materials -= cost
                    if random.random() <= chance: item.upgrade(); self.add_message(f"success! {item.name}.")
                    else: self.add_message(f"failed! shards lost.")

    def handle_combat_input(self, key):
        if self.battle_system.turn == "player":
            if key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                if self.battle_system.menu_state in ["magic", "items"]: self.battle_system.menu_state = "main"; return
            if key in [pygame.K_UP, pygame.K_w]:
                if self.battle_system.menu_state == "main": self.battle_system.selected_option = (self.battle_system.selected_option - 1) % len(self.battle_system.options)
                elif self.battle_system.menu_state == "magic": self.battle_system.magic_selected_option = (self.battle_system.magic_selected_option - 1) % (len(self.player.spells) + 1)
                elif self.battle_system.menu_state == "items":
                    consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
                    self.battle_system.item_selected_option = (self.battle_system.item_selected_option - 1) % (len(consumables) + 1)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                if self.battle_system.menu_state == "main": self.battle_system.selected_option = (self.battle_system.selected_option + 1) % len(self.battle_system.options)
                elif self.battle_system.menu_state == "magic": self.battle_system.magic_selected_option = (self.battle_system.magic_selected_option + 1) % (len(self.player.spells) + 1)
                elif self.battle_system.menu_state == "items":
                    consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
                    self.battle_system.item_selected_option = (self.battle_system.item_selected_option + 1) % (len(consumables) + 1)
            elif key == pygame.K_RETURN:
                res = self.battle_system.execute_player_action()
                if res == "victory":
                    self.add_message(self.battle_system.player_msg)
                    if self.player.gain_experience(self.battle_system.enemy.exp_reward):
                        self.player.level_up(); self.state = state_level_up
                    else: self.state = state_exploration
                    self.battle_system.enemy.kill()
                elif res == "flee_success":
                    self.state = state_exploration; self.player.rect.x, self.player.rect.y = self.last_x, self.last_y

    def check_collisions(self):
        hit_e = pygame.sprite.spritecollideany(self.player, self.enemies)
        if hit_e: self.state = state_combat; self.battle_system.start_battle(self.player, hit_e)
        hit_c = pygame.sprite.spritecollideany(self.player, self.chests)
        if hit_c: self.add_message(hit_c.open(self.player)); hit_c.kill()
        hit_f = pygame.sprite.spritecollideany(self.player, self.forges)
        if hit_f: self.state = "forge"; self.forge_selection = 0
        portal = pygame.sprite.spritecollideany(self.player, self.exits)
        if portal:
            if len(self.enemies) == 0:
                if self.current_stage % 5 == 0:
                    self.state = state_shop; self.shop_items = self.generate_shop_items()
                    self.player.passive_points += 1; self.add_message("boss defeated! gained 1 passive point.")
                self.current_stage += 1; self.generate_stage(); self.player.rect.topleft = (64, 64)
            else: self.add_message(f"portal locked! {len(self.enemies)} monsters remain.")

    def draw_ui_panel(self, title):
        panel_rect = pygame.Rect(100, 100, 600, 420)
        pygame.draw.rect(self.screen, (20, 20, 20), panel_rect)
        pygame.draw.rect(self.screen, white, panel_rect, 2)
        self.screen.blit(self.font_sub.render(title, True, gold), (120, 115))

    def draw_bar(self, x, y, curr, max_v, col, lab):
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, 140, 12))
        fill = (curr / max_v) * 140 if max_v > 0 else 0
        pygame.draw.rect(self.screen, col, (x, y, fill, 12))
        pygame.draw.rect(self.screen, white, (x, y, 140, 12), 1)
        self.screen.blit(self.font_tiny.render(f"{lab}: {int(curr)}/{int(max_v)}", True, white), (x, y - 16))

    def draw_hud(self):
        # Draw HUD at the top
        hud_bg = pygame.Surface((width, 70))
        hud_bg.set_alpha(180)
        hud_bg.fill((20, 20, 20))
        self.screen.blit(hud_bg, (0, 0))
        
        # Draw Combat/Event Log at the bottom so it doesn't overlap movement
        log_bg = pygame.Surface((width, 80))
        log_bg.set_alpha(180)
        log_bg.fill((20, 20, 20))
        self.screen.blit(log_bg, (0, height - 80))
        
        # Render log messages
        for i, m in enumerate(self.messages[-3:]): # Only show last 3 to save space
            txt = self.font_tiny.render(m, True, white)
            self.screen.blit(txt, (20, height - 70 + (i * 20)))

    def draw_inventory(self):
        self.draw_ui_panel("INVENTORY")
        self.screen.blit(self.font_tiny.render("L/R: switch | ENTER: equip | X: dismantle | SPACE: auto", True, (200, 200, 200)), (120, 145))
        c_eq = gold if self.inv_tab == "equipped" else (100, 255, 100)
        c_bg = gold if self.inv_tab == "bag" else (100, 100, 255)
        self.screen.blit(self.font_tiny.render("EQUIPPED:", True, c_eq), (120, 175))
        y = 200; eq_slots = list(self.player.inventory.equipped.keys())
        for i, slot in enumerate(eq_slots):
            item = self.player.inventory.equipped[slot]; name = item.name if item else "empty"
            px = "> " if self.inv_tab == "equipped" and i == self.inv_selection else "  "
            self.screen.blit(self.font_tiny.render(f"{px}{slot.upper()}: {name}", True, white), (130, y)); y += 22
        y = 175; self.screen.blit(self.font_tiny.render("BAG:", True, c_bg), (400, y)); y += 25
        visible_limit = 7
        for i in range(self.inv_bag_scroll, min(len(self.player.inventory.bag), self.inv_bag_scroll + visible_limit)):
            item = self.player.inventory.bag[i]; px = "> " if self.inv_tab == "bag" and i == self.inv_selection else "  "
            qty = f" (x{item.quantity})" if item.quantity > 1 else ""
            self.screen.blit(self.font_tiny.render(f"{px}{item.name}{qty}", True, white), (410, y)); y += 22
        
        h_item = None
        if self.inv_tab == "equipped" and self.inv_selection < len(eq_slots): h_item = self.player.inventory.equipped[eq_slots[self.inv_selection]]
        elif self.inv_tab == "bag" and self.inv_selection < len(self.player.inventory.bag): h_item = self.player.inventory.bag[self.inv_selection]
        if h_item:
            pygame.draw.rect(self.screen, (40, 40, 40), (120, 360, 560, 140)); pygame.draw.rect(self.screen, gold, (120, 360, 560, 140), 1)
            self.screen.blit(self.font_tiny.render(h_item.name.upper(), True, gold), (130, 370))
            self.screen.blit(self.font_tiny.render(h_item.description, True, white), (130, 395))
            if h_item.item_type == "equipment":
                # SPEED +-1 FIX: Using conditional string building so negatives format cleanly
                stat_texts = []
                for k, v in h_item.stats.items():
                    val_str = f"+{v}" if v > 0 else str(v)
                    stat_texts.append(f"{k.replace('_', ' ').upper()}: {val_str}")
                s_str = " | ".join(stat_texts)
                if getattr(h_item, "element_damage", 0) > 0: s_str += f" | {h_item.element.upper()}: +{h_item.element_damage}"
                self.screen.blit(self.font_tiny.render(f"STATS: {s_str}", True, (100, 255, 100)), (130, 420))
            elif h_item.item_type == "consumable":
                self.screen.blit(self.font_tiny.render(f"EFFECT: {h_item.effect_type.upper()} {h_item.amount}", True, (100, 100, 255)), (130, 420))

    def draw_info_screen(self):
        self.draw_ui_panel("CHARACTER STATUS")
        stats = [f"CLASS: {self.player.player_class.upper()}", f"ATK: {self.player.attack_damage}", f"MAG: {self.player.magic_damage}", f"ARM: {self.player.armor}", f"SPD: {self.player.speed}", f"GOLD: {self.player.gold}"]
        y = 160
        for s in stats: self.screen.blit(self.font_tiny.render(s, True, white), (120, y)); y += 25
        y = 160; self.screen.blit(self.font_tiny.render("PASSIVES:", True, (100, 255, 100)), (400, y)); y += 25
        for s in self.player.unlocked_skills: self.screen.blit(self.font_tiny.render(f"- {s.name.upper()}", True, white), (420, y)); y += 20

    def draw_level_up_screen(self):
        txt = "ATTRIBUTES" if self.level_up_tab == "stats" else ("PASSIVES" if self.level_up_tab == "skills" else "SPELLS")
        pts = self.player.attribute_points if self.level_up_tab == "stats" else (self.player.passive_points if self.level_up_tab == "skills" else self.player.spell_points)
        self.draw_ui_panel(f"UPGRADE {txt} ({pts} PTS)")
        self.screen.blit(self.font_tiny.render("TAB: switch menu | ESC: close", True, (200, 200, 200)), (120, 145))
        if self.level_up_tab == "stats":
            for i, o in enumerate(self.level_up_options):
                c = gold if i == self.level_up_selection else white
                self.screen.blit(self.font_sub.render(o.replace("_"," ").upper(), True, c), (150, 190 + i * 45))
        elif self.level_up_tab == "skills":
            for i, skey in enumerate(self.skill_options):
                skill = skill_tree_database[skey]; col = (100, 255, 100) if skill in self.player.unlocked_skills else (gold if i == self.level_up_selection else white)
                self.screen.blit(self.font_sub.render(f"{skill.name.upper()} ({skill.cost}p)", True, col), (150, 190 + i * 45))
                if i == self.level_up_selection: self.screen.blit(self.font_tiny.render(skill.description, True, (200, 200, 200)), (150, 220 + i * 45))
        elif self.level_up_tab == "spells":
            pool = class_spell_pools[self.player.player_class]
            for i, sp_name in enumerate(pool):
                learned = next((s for s in self.player.spells if s.name == sp_name), None)
                col = gold if i == self.level_up_selection else white
                lvl_txt = f"LVL {learned.level}/5" if learned else "UNLEARNED"
                self.screen.blit(self.font_sub.render(f"{sp_name.upper()} [{lvl_txt}]", True, col), (150, 190 + i * 45))

    def draw_shop(self):
        self.draw_ui_panel(f"MERCHANT - {self.player.gold} GOLD")
        c_buy = gold if self.shop_tab == "buy" else (100, 255, 100); c_sell = gold if self.shop_tab == "sell" else (255, 100, 100)
        y = 175; self.screen.blit(self.font_tiny.render("BUY:", True, c_buy), (120, y)); y += 25
        for i, skey in enumerate(self.shop_items):
            color = gold if self.shop_tab == "buy" and i == self.shop_selection else white
            self.screen.blit(self.font_tiny.render(f"{item_database[skey].name.upper()} ({50 * self.current_stage}g)", True, color), (130, y)); y += 22
        y = 175; self.screen.blit(self.font_tiny.render("SELL:", True, c_sell), (400, y)); y += 25
        sellables = [{"source": "equipped", "slot": k, "item": v} for k,v in self.player.inventory.equipped.items() if v] + [{"source": "bag", "index": i, "item": v} for i,v in enumerate(self.player.inventory.bag)]
        for i in range(self.shop_sell_scroll, min(len(sellables), self.shop_sell_scroll + 7)):
            s = sellables[i]; color = gold if self.shop_tab == "sell" and i == self.shop_selection else white
            eq = " [EQ]" if s["source"] == "equipped" else ""
            self.screen.blit(self.font_tiny.render(f"{s['item'].name.upper()}{eq} (+{20 * self.current_stage}g)", True, color), (410, y)); y += 22

    def draw_forge(self):
        self.draw_ui_panel(f"THE FORGE - {self.player.forge_materials} SHARDS")
        forgeables = [i for i in self.player.inventory.bag if i.item_type == "equipment"]
        y = 180
        if not forgeables: self.screen.blit(self.font_tiny.render("no items to upgrade.", True, white), (130, y)); return
        for i in range(self.forge_scroll, min(len(forgeables), 10)):
            item = forgeables[i]; color = gold if i == self.forge_selection else white
            cost = 1 + (item.upgrade_level * 2); chance = int(max(0.1, 1.0 - (item.upgrade_level * 0.08)) * 100)
            txt = f"{item.name} [COST: {cost} | {chance}%]" if item.upgrade_level < 10 else f"{item.name} [MAX]"
            self.screen.blit(self.font_tiny.render(txt, True, color), (130, y)); y += 22

    def update(self):
        # Allow the player sprite to animate regardless of state
        if self.player:
            self.player.update_animation()
            
        if self.state == state_exploration:
            now = pygame.time.get_ticks()
            if not hasattr(self, 'last_move'): self.last_move = now
            if now - self.last_move > 500:
                for e in self.enemies: e.map_wander(self.game_map, 64)
                self.last_move = now
                self.check_collisions()
        # ... rest of the combat logic ...
        elif self.state == state_combat and self.battle_system.turn == "enemy":
            self.draw()
            pygame.time.delay(500)
            res = self.battle_system.execute_enemy_turn()
            if res == "defeat": 
                self.running = False
            elif res == "victory":
                self.add_message(self.battle_system.player_msg)
                if self.player.gain_experience(self.battle_system.enemy.exp_reward):
                    self.player.level_up()
                    self.state = state_level_up
                else: 
                    self.state = state_exploration
                self.battle_system.enemy.kill()
            pygame.event.clear(pygame.KEYDOWN)

    def draw(self):
        self.screen.fill(black)
        if self.state == state_main_menu:
            title = self.font_main.render("RETRO RPG", True, gold)
            self.screen.blit(title, (width//2 - title.get_width()//2, 100))
            for i, o in enumerate(self.menu_options):
                c = gold if i == self.menu_selection else white
                self.screen.blit(self.font_sub.render(o.upper(), True, c), (width//2 - 100, 300 + i * 60))
        elif self.state == state_naming:
            self.screen.blit(self.font_sub.render("ENTER NAME:", True, white), (100, 200))
            self.screen.blit(self.font_main.render(self.temp_name + "_", True, gold), (100, 300))
        elif self.state == state_class_select:
            self.screen.blit(self.font_sub.render("CHOOSE CLASS:", True, white), (100, 100))
            for i, c in enumerate(self.class_options):
                col = gold if i == self.class_selection else white
                self.screen.blit(self.font_sub.render(c.upper(), True, col), (100, 200 + i * 60))
        if self.state in [state_exploration, state_inventory, state_level_up, state_shop, "forge"]:
            # 1. CALCULATE CAMERA
            # Centers the camera on the player
            cam_x = self.player.rect.centerx - (width // 2)
            cam_y = self.player.rect.centery - (height // 2)
            
            # 2. DRAW WORLD (Offset by Camera)
            self.game_map.draw(self.screen, cam_x, cam_y)
            
            for sprite in self.exits: 
                self.screen.blit(sprite.image, (sprite.rect.x - cam_x, sprite.rect.y - cam_y))
            for sprite in self.chests: 
                self.screen.blit(sprite.image, (sprite.rect.x - cam_x, sprite.rect.y - cam_y))
            for sprite in self.forges: 
                self.screen.blit(sprite.image, (sprite.rect.x - cam_x, sprite.rect.y - cam_y))
            for sprite in self.enemies: 
                self.screen.blit(sprite.image, (sprite.rect.x - cam_x, sprite.rect.y - cam_y))
            
            # Player is now 96x96, offset drawing to center on his 64x64 hitbox
            self.screen.blit(self.player.image, (self.player.rect.x - cam_x - 16, self.player.rect.y - cam_y - 16))
            
            # 3. DRAW UI OVERLAYS (No Camera Offset)
            self.draw_hud()
            
            if self.state == state_inventory:
                self.draw_inventory()
                # Draw the portrait in the inventory box
                self.player.draw_large_portrait(self.screen, 130, 200)
            elif self.state == state_shop: self.draw_shop()
            
        elif self.state == state_combat:
            self.battle_system.draw()
        pygame.display.flip()

    def run(self):
        while self.running: self.handle_events(); self.update(); self.draw(); self.clock.tick(fps)
        pygame.quit(); sys.exit()