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
        
        self.player.level = p_data["level"]
        self.player.experience = p_data["exp"]
        self.player.exp_to_next_level = p_data["exp_next"]
        
        self.player.attribute_points = p_data.get("attribute_points", p_data.get("stat_points", 0))
        self.player.spell_points = p_data.get("spell_points", p_data.get("skill_points", 0))
        self.player.passive_points = p_data.get("passive_points", 0)
        
        self.player.max_health = p_data["max_hp"]
        self.player.current_health = p_data["hp"]
        self.player.max_mana = p_data["max_mp"]
        self.player.current_mana = p_data["mp"]
        self.player.attack_damage = p_data["attack"]
        self.player.magic_damage = p_data["magic"]
        self.player.armor = p_data["armor"]
        self.player.speed = p_data["speed"]
        self.player.gold = p_data["gold"]
        self.player.forge_materials = p_data.get("forge_materials", 0)
        
        self.player.unlocked_skills = [skill_tree_database[s] for s in p_data["skills"]]
        
        self.player.spells = []
        for sp in p_data["spells"]:
            spell_obj = copy.deepcopy(spell_database[sp["name"]])
            spell_obj.level = sp["level"]
            self.player.spells.append(spell_obj)
            
        self.player.inventory.bag = []
        for b_item in p_data["bag"]:
            if isinstance(b_item, dict):
                new_item = copy.deepcopy(item_database[b_item.get("original_name", b_item["name"])])
                new_item.quantity = b_item.get("quantity", 1)
                upgrades = b_item.get("upgrade", 0)
                if hasattr(new_item, "upgrade"):
                    for _ in range(upgrades): new_item.upgrade()
                self.player.inventory.bag.append(new_item)
            else:
                new_item = copy.deepcopy(item_database[b_item])
                new_item.quantity = 1
                self.player.inventory.bag.append(new_item)
                
        for slot, item_data in p_data["equipped"].items():
            if item_data:
                if isinstance(item_data, dict):
                    new_item = copy.deepcopy(item_database[item_data["name"]])
                    new_item.quantity = 1
                    upgrades = item_data.get("upgrade", 0)
                    if hasattr(new_item, "upgrade"):
                        for _ in range(upgrades): new_item.upgrade()
                    self.player.inventory.equipped[slot] = new_item
                else:
                    new_item = copy.deepcopy(item_database[item_data])
                    new_item.quantity = 1
                    self.player.inventory.equipped[slot] = new_item
            else: 
                self.player.inventory.equipped[slot] = None
                
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
        self.enemies.empty()
        self.chests.empty()
        self.forges.empty()
        self.exits.empty()
        
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
            else:
                self.add_message("no unspent points available.")
        
        if self.game_map.is_walkable(nx, ny):
            self.last_x = self.player.rect.x
            self.last_y = self.player.rect.y
            self.player.rect.x, self.player.rect.y = nx, ny
            self.check_collisions()

    def handle_inventory_input(self, key):
        if key in [pygame.K_i, pygame.K_ESCAPE]:
            self.state = state_exploration
            return
            
        if key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]:
            self.inv_tab = "bag" if self.inv_tab == "equipped" else "equipped"
            self.inv_selection = 0
            self.inv_bag_scroll = 0
            
        eq_list = list(self.player.inventory.equipped.keys())
        limit = len(eq_list) if self.inv_tab == "equipped" else len(self.player.inventory.bag)
        
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.inv_selection = (self.inv_selection - 1) % limit
                if self.inv_tab == "bag":
                    if self.inv_selection < self.inv_bag_scroll:
                        self.inv_bag_scroll = self.inv_selection
                    elif self.inv_selection >= self.inv_bag_scroll + 7:
                        self.inv_bag_scroll = max(0, self.inv_selection - 6)
                        
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.inv_selection = (self.inv_selection + 1) % limit
                if self.inv_tab == "bag":
                    if self.inv_selection >= self.inv_bag_scroll + 7:
                        self.inv_bag_scroll = self.inv_selection - 6
                    elif self.inv_selection < self.inv_bag_scroll:
                        self.inv_bag_scroll = self.inv_selection
                        
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
                            self.player.inventory.remove_item(item)
                            self.add_message(msg)
                            self.inv_selection = 0
                            self.inv_bag_scroll = 0
                            
            elif key == pygame.K_x:
                if self.inv_tab == "bag":
                    item = self.player.inventory.bag[self.inv_selection]
                    if item.item_type == "equipment":
                        mats = {"common": 1, "uncommon": 2, "rare": 4, "epic": 8, "legendary": 15}.get(item.rarity, 1)
                        mats += (item.upgrade_level * 2)
                        self.player.forge_materials += mats
                        self.player.inventory.remove_item(item)
                        self.add_message(f"dismantled {item.name} for {mats} shards.")
                        limit = len(self.player.inventory.bag)
                        if limit == 0:
                            self.inv_selection = 0
                            self.inv_bag_scroll = 0
                        elif self.inv_selection >= limit:
                            self.inv_selection = limit - 1
                            
        if key == pygame.K_SPACE:
            self.player.inventory.auto_equip(self.player)
            self.add_message("optimized gear equipped.")
            # Clamp the bounds after auto equip modifies the bag to prevent the IndexError crash
            limit = len(self.player.inventory.equipped) if self.inv_tab == "equipped" else len(self.player.inventory.bag)
            if limit == 0:
                self.inv_selection = 0
                self.inv_bag_scroll = 0
            elif self.inv_selection >= limit:
                self.inv_selection = limit - 1

    def handle_level_up_input(self, key):
        if key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            self.state = state_exploration
            return

        if key == pygame.K_TAB:
            tabs = ["stats", "skills", "spells"]
            curr_idx = tabs.index(self.level_up_tab)
            self.level_up_tab = tabs[(curr_idx + 1) % 3]
            self.level_up_selection = 0
            return

        pool = class_spell_pools[self.player.player_class]
        if self.level_up_tab == "stats": limit = len(self.level_up_options)
        elif self.level_up_tab == "skills": limit = len(self.skill_options)
        else: limit = len(pool)
        
        if key in [pygame.K_UP, pygame.K_w]: self.level_up_selection = (self.level_up_selection - 1) % limit
        elif key in [pygame.K_DOWN, pygame.K_s]: self.level_up_selection = (self.level_up_selection + 1) % limit
        elif key == pygame.K_RETURN:
            if self.level_up_tab == "stats" and self.player.attribute_points >= 1:
                stat = self.level_up_options[self.level_up_selection]
                if stat in ["max_health", "max_mana"]: setattr(self.player, stat, getattr(self.player, stat) + 20)
                else: setattr(self.player, stat, getattr(self.player, stat) + 2)
                self.player.attribute_points -= 1
            elif self.level_up_tab == "skills":
                s_key = self.skill_options[self.level_up_selection]
                skill = skill_tree_database[s_key]
                if skill not in self.player.unlocked_skills and self.player.passive_points >= skill.cost:
                    self.player.passive_points -= skill.cost
                    self.player.unlocked_skills.append(skill)
                    self.add_message(f"trait unlocked: {skill.name.upper()}")
            elif self.level_up_tab == "spells" and self.player.spell_points >= 1:
                spell_name = pool[self.level_up_selection]
                learned = next((s for s in self.player.spells if s.name == spell_name), None)
                if learned:
                    if learned.level < learned.max_level:
                        learned.level += 1
                        self.player.spell_points -= 1
                        self.add_message(f"upgraded {spell_name} to lvl {learned.level}.")
                else:
                    if len(self.player.spells) < 4:
                        self.player.spells.append(copy.deepcopy(spell_database[spell_name]))
                        self.player.spell_points -= 1
                        self.add_message(f"learned {spell_name}.")
                    else:
                        self.add_message("spell slots full (max 4).")

    def generate_shop_items(self):
        items = ["major health potion", "major mana potion"]
        
        warrior_pool = ["broadsword", "steel claymore", "flame sword", "dragon slayer", "chainmail", "plate armor", "obsidian band"]
        mage_pool = ["sage wand", "archmage scepter", "wizard robe", "elder cloak", "topaz ring", "sapphire necklace"]
        rogue_pool = ["obsidian dagger", "frost dagger", "shadow fang", "leather tunic", "shadow cloak", "emerald band"]
        archer_pool = ["longbow", "venom spear", "storm bow", "hunter tunic", "emerald band", "ruby ring"]
        
        pool = []
        if self.player.player_class == "warrior": pool = warrior_pool
        elif self.player.player_class == "mage": pool = mage_pool
        elif self.player.player_class == "rogue": pool = rogue_pool
        elif self.player.player_class == "archer": pool = archer_pool
            
        if pool: items.extend(random.sample(pool, min(3, len(pool))))
        return items

    def get_sellable_items(self):
        items = []
        for slot, item in self.player.inventory.equipped.items():
            if item: items.append({"source": "equipped", "slot": slot, "item": item})
        for i, item in enumerate(self.player.inventory.bag):
            items.append({"source": "bag", "index": i, "item": item})
        return items

    def handle_shop_input(self, key):
        if self.shop_confirm_sell:
            if key == pygame.K_y:
                item = self.shop_confirm_sell["item"]
                slot = self.shop_confirm_sell["slot"]
                val = 20 * self.current_stage
                self.player.inventory.unequip(slot, self.player)
                self.player.inventory.remove_item(item)
                self.player.gold += val
                self.add_message(f"sold equipped {item.name} for {val}g.")
                self.shop_confirm_sell = None
                self.shop_selection = 0
                self.shop_sell_scroll = 0
            elif key in [pygame.K_n, pygame.K_ESCAPE]:
                self.shop_confirm_sell = None
            return

        if key in [pygame.K_ESCAPE, pygame.K_SPACE]:
            self.state = state_exploration
            return
            
        if key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]:
            self.shop_tab = "sell" if self.shop_tab == "buy" else "buy"
            self.shop_selection = 0
            self.shop_sell_scroll = 0
            return
            
        sellables = self.get_sellable_items()
        limit = len(self.shop_items) if self.shop_tab == "buy" else len(sellables)
        
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.shop_selection = (self.shop_selection - 1) % limit
                if self.shop_tab == "sell":
                    if self.shop_selection < self.shop_sell_scroll:
                        self.shop_sell_scroll = self.shop_selection
                    elif self.shop_selection >= self.shop_sell_scroll + 7:
                        self.shop_sell_scroll = max(0, self.shop_selection - 6)
                        
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.shop_selection = (self.shop_selection + 1) % limit
                if self.shop_tab == "sell":
                    if self.shop_selection >= self.shop_sell_scroll + 7:
                        self.shop_sell_scroll = self.shop_selection - 6
                    elif self.shop_selection < self.shop_sell_scroll:
                        self.shop_sell_scroll = self.shop_selection
                        
            elif key == pygame.K_RETURN:
                if self.shop_tab == "buy":
                    from items.equipment import item_database
                    ikey = self.shop_items[self.shop_selection]
                    cost = 50 * self.current_stage
                    if self.player.gold >= cost:
                        self.player.gold -= cost
                        self.player.inventory.add_item(item_database[ikey])
                        self.add_message(f"purchased {item_database[ikey].name}.")
                    else:
                        self.add_message("not enough gold!")
                elif self.shop_tab == "sell":
                    sell_info = sellables[self.shop_selection]
                    if sell_info["source"] == "equipped":
                        self.shop_confirm_sell = sell_info
                    else:
                        item = sell_info["item"]
                        val = 20 * self.current_stage
                        self.player.gold += val
                        self.player.inventory.remove_item(item)
                        self.add_message(f"sold {item.name} for {val}g.")
                        
                        limit = len(self.get_sellable_items())
                        if limit == 0:
                            self.shop_selection = 0
                            self.shop_sell_scroll = 0
                        elif self.shop_selection >= limit:
                            self.shop_selection = limit - 1
                            if self.shop_selection < self.shop_sell_scroll:
                                self.shop_sell_scroll = self.shop_selection

    def handle_forge_input(self, key):
        if key in [pygame.K_ESCAPE, pygame.K_SPACE]:
            self.state = state_exploration
            self.player.rect.x = getattr(self, "last_x", self.player.rect.x)
            self.player.rect.y = getattr(self, "last_y", self.player.rect.y)
            return

        forgeables = [i for i in self.player.inventory.bag if i.item_type == "equipment"]
        limit = len(forgeables)
        
        if limit > 0:
            if key in [pygame.K_UP, pygame.K_w]:
                self.forge_selection = (self.forge_selection - 1) % limit
                if self.forge_selection < self.forge_scroll:
                    self.forge_scroll = self.forge_selection
                elif self.forge_selection >= self.forge_scroll + 10:
                    self.forge_scroll = max(0, self.forge_selection - 9)
            elif key in [pygame.K_DOWN, pygame.K_s]:
                self.forge_selection = (self.forge_selection + 1) % limit
                if self.forge_selection >= self.forge_scroll + 10:
                    self.forge_scroll = self.forge_selection - 9
                elif self.forge_selection < self.forge_scroll:
                    self.forge_scroll = self.forge_selection
            elif key == pygame.K_RETURN:
                item = forgeables[self.forge_selection]
                cost = 1 + (item.upgrade_level * 2)
                chance = max(0.1, 1.0 - (item.upgrade_level * 0.08))
                
                if item.upgrade_level >= 10:
                    self.add_message("item is already at max level!")
                elif self.player.forge_materials >= cost:
                    self.player.forge_materials -= cost
                    if random.random() <= chance:
                        item.upgrade()
                        self.add_message(f"forge success! upgraded to {item.name}.")
                    else:
                        self.add_message(f"forge failed! {cost} shards lost.")
                else:
                    self.add_message(f"not enough shards. need {cost}.")

    def handle_combat_input(self, key):
        if self.battle_system.turn == "player":
            if key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                if self.battle_system.menu_state in ["magic", "items"]:
                    self.battle_system.menu_state = "main"
                return

            if key in [pygame.K_UP, pygame.K_w]:
                if self.battle_system.menu_state == "main":
                    self.battle_system.selected_option = (self.battle_system.selected_option - 1) % len(self.battle_system.options)
                elif self.battle_system.menu_state == "magic":
                    limit = len(self.player.spells) + 1
                    self.battle_system.magic_selected_option = (self.battle_system.magic_selected_option - 1) % limit
                elif self.battle_system.menu_state == "items":
                    consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
                    limit = len(consumables) + 1
                    self.battle_system.item_selected_option = (self.battle_system.item_selected_option - 1) % limit
            elif key in [pygame.K_DOWN, pygame.K_s]:
                if self.battle_system.menu_state == "main":
                    self.battle_system.selected_option = (self.battle_system.selected_option + 1) % len(self.battle_system.options)
                elif self.battle_system.menu_state == "magic":
                    limit = len(self.player.spells) + 1
                    self.battle_system.magic_selected_option = (self.battle_system.magic_selected_option + 1) % limit
                elif self.battle_system.menu_state == "items":
                    consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
                    limit = len(consumables) + 1
                    self.battle_system.item_selected_option = (self.battle_system.item_selected_option + 1) % limit
            elif key == pygame.K_RETURN:
                res = self.battle_system.execute_player_action()
                if res == "victory":
                    self.add_message(self.battle_system.player_msg)
                    if self.player.gain_experience(self.battle_system.enemy.exp_reward):
                        self.player.level_up()
                        self.state = state_level_up
                    else: self.state = state_exploration
                    self.battle_system.enemy.kill()
                elif res == "flee_success":
                    self.state = state_exploration
                    self.player.rect.x = getattr(self, "last_x", self.player.rect.x)
                    self.player.rect.y = getattr(self, "last_y", self.player.rect.y)
                    self.add_message("successfully escaped combat!")

    def check_collisions(self):
        hit_e = pygame.sprite.spritecollideany(self.player, self.enemies)
        if hit_e:
            self.state = state_combat
            self.battle_system.start_battle(self.player, hit_e)
        
        hit_c = pygame.sprite.spritecollideany(self.player, self.chests)
        if hit_c:
            self.add_message(hit_c.open(self.player))
            hit_c.kill()
            
        hit_f = pygame.sprite.spritecollideany(self.player, self.forges)
        if hit_f:
            self.state = "forge"
            self.forge_selection = 0
            self.forge_scroll = 0
            
        portal = pygame.sprite.spritecollideany(self.player, self.exits)
        if portal:
            if len(self.enemies) == 0:
                if self.current_stage % 5 == 0:
                    self.state = state_shop
                    self.shop_items = self.generate_shop_items()
                    self.shop_selection = 0
                    self.shop_tab = "buy"
                    self.shop_sell_scroll = 0
                    
                    self.player.passive_points += 1
                    self.add_message("boss defeated! gained 1 passive point.")
                    
                self.current_stage += 1
                self.generate_stage()
                self.last_x, self.last_y = 64, 64
                self.player.rect.topleft = (64, 64)
            else: self.add_message(f"portal locked! {len(self.enemies)} enemies remain.")

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
        # Increased height and repositioned text to avoid colliding with status bars
        hud_bg = pygame.Surface((width, 80))
        hud_bg.set_alpha(180)
        hud_bg.fill(black)
        self.screen.blit(hud_bg, (0, 0))
        
        name_txt = self.font_sub.render(f"LVL {self.player.level} {self.player.player_class.upper()}", True, gold)
        self.screen.blit(name_txt, (15, 15))
        self.screen.blit(self.font_tiny.render(f"F5: save | L: stats | GOLD: {self.player.gold} | SHARDS: {self.player.forge_materials}", True, (200, 200, 200)), (15, 50))
        
        # Shifted bars rightwards to give the text proper margins
        self.draw_bar(320, 20, self.player.current_health, self.player.max_health, (200, 50, 50), "HP")
        self.draw_bar(480, 20, self.player.current_mana, self.player.max_mana, (50, 50, 200), "MP")
        self.draw_bar(640, 20, self.player.experience, self.player.exp_to_next_level, (200, 200, 50), "EXP")
        
        log_bg = pygame.Surface((width, 100)); log_bg.set_alpha(150); log_bg.fill(black); self.screen.blit(log_bg, (0, height - 100))
        for i, m in enumerate(self.messages):
            self.screen.blit(self.font_tiny.render(m, True, white), (20, height - 90 + (i * 18)))

    def draw_inventory(self):
        self.draw_ui_panel("INVENTORY")
        self.screen.blit(self.font_tiny.render("L/R: switch | ENTER: equip | X: dismantle | SPACE: auto", True, (200, 200, 200)), (120, 145))
        
        c_eq = gold if self.inv_tab == "equipped" else (100, 255, 100)
        c_bg = gold if self.inv_tab == "bag" else (100, 100, 255)
        
        self.screen.blit(self.font_tiny.render("EQUIPPED:", True, c_eq), (120, 175))
        y = 200
        eq_slots = list(self.player.inventory.equipped.keys())
        for i, slot in enumerate(eq_slots):
            item = self.player.inventory.equipped[slot]
            name = item.name if item else "empty"
            px = "> " if self.inv_tab == "equipped" and i == self.inv_selection else "  "
            self.screen.blit(self.font_tiny.render(f"{px}{slot.upper()}: {name}", True, white), (130, y)); y += 22
            
        y = 175
        self.screen.blit(self.font_tiny.render("BAG:", True, c_bg), (400, y))
        y += 25
        
        visible_limit = 7
        for i in range(self.inv_bag_scroll, min(len(self.player.inventory.bag), self.inv_bag_scroll + visible_limit)):
            item = self.player.inventory.bag[i]
            px = "> " if self.inv_tab == "bag" and i == self.inv_selection else "  "
            qty = f" (x{item.quantity})" if hasattr(item, 'quantity') and item.quantity > 1 else ""
            self.screen.blit(self.font_tiny.render(f"{px}{item.name}{qty}", True, white), (410, y)); y += 22
            
        if len(self.player.inventory.bag) > self.inv_bag_scroll + visible_limit:
            self.screen.blit(self.font_tiny.render("  ...", True, white), (410, y))

        h_item = None
        if self.inv_tab == "equipped" and len(eq_slots) > 0: 
            h_item = self.player.inventory.equipped[eq_slots[self.inv_selection]]
        elif self.inv_tab == "bag" and len(self.player.inventory.bag) > 0: 
            h_item = self.player.inventory.bag[self.inv_selection]
        
        if h_item:
            pygame.draw.rect(self.screen, (40, 40, 40), (120, 360, 560, 140))
            pygame.draw.rect(self.screen, gold, (120, 360, 560, 140), 1)
            self.screen.blit(self.font_tiny.render(h_item.name.upper(), True, gold), (130, 370))
            self.screen.blit(self.font_tiny.render(h_item.description, True, white), (130, 395))
            
            if h_item.item_type == "equipment":
                # using the native python sign formatter `:+d` instead of concatenating '+'
                s_str = " | ".join([f"{k.replace('_', ' ').upper()}: {v:+d}" for k, v in h_item.stats.items()])
                if getattr(h_item, "element_damage", 0) > 0:
                    s_str += f" | {h_item.element.upper()}: +{h_item.element_damage}"
                self.screen.blit(self.font_tiny.render(f"STATS: {s_str}", True, (100, 255, 100)), (130, 420))
            elif h_item.item_type == "consumable":
                self.screen.blit(self.font_tiny.render(f"EFFECT: {h_item.effect_type.upper()} {h_item.amount}", True, (100, 100, 255)), (130, 420))

    def draw_info_screen(self):
        self.draw_ui_panel("CHARACTER STATUS")
        stats = [f"CLASS: {self.player.player_class.upper()}", f"ATK: {self.player.attack_damage}", f"MAG: {self.player.magic_damage}", f"ARM: {self.player.armor}", f"SPD: {self.player.speed}", f"GOLD: {self.player.gold}"]
        y = 160
        for s in stats: self.screen.blit(self.font_tiny.render(s, True, white), (120, y)); y += 25
        y = 160
        self.screen.blit(self.font_tiny.render("PASSIVES:", True, (100, 255, 100)), (400, y)); y += 25
        for s in self.player.unlocked_skills: self.screen.blit(self.font_tiny.render(f"- {s.name.upper()}", True, white), (420, y)); y += 20

    def draw_level_up_screen(self):
        txt = "ATTRIBUTES" if self.level_up_tab == "stats" else ("PASSIVES" if self.level_up_tab == "skills" else "SPELLS")
        
        if self.level_up_tab == "stats":
            pts = self.player.attribute_points
        elif self.level_up_tab == "skills":
            pts = self.player.passive_points
        else:
            pts = self.player.spell_points
            
        self.draw_ui_panel(f"UPGRADE {txt} ({pts} PTS)")
        self.screen.blit(self.font_tiny.render("TAB: switch menu | ESC: save & close", True, (200, 200, 200)), (120, 145))
        
        if self.level_up_tab == "stats":
            for i, o in enumerate(self.level_up_options):
                c = gold if i == self.level_up_selection else white
                self.screen.blit(self.font_sub.render(o.replace("_"," ").upper(), True, c), (150, 190 + i * 45))
        elif self.level_up_tab == "skills":
            for i, skey in enumerate(self.skill_options):
                skill = skill_tree_database[skey]
                if skill in self.player.unlocked_skills: col = (100, 255, 100)
                elif i == self.level_up_selection: col = gold
                else: col = white
                self.screen.blit(self.font_sub.render(f"{skill.name.upper()} ({skill.cost}p)", True, col), (150, 190 + i * 45))
                if i == self.level_up_selection:
                    self.screen.blit(self.font_tiny.render(skill.description, True, (200, 200, 200)), (150, 220 + i * 45))
        elif self.level_up_tab == "spells":
            pool = class_spell_pools[self.player.player_class]
            for i, sp_name in enumerate(pool):
                learned = next((s for s in self.player.spells if s.name == sp_name), None)
                if learned and learned.level >= learned.max_level: col = (100, 255, 100)
                elif i == self.level_up_selection: col = gold
                else: col = white
                lvl_txt = f"LVL {learned.level}/5" if learned else "UNLEARNED"
                self.screen.blit(self.font_sub.render(f"{sp_name.upper()} [{lvl_txt}]", True, col), (150, 190 + i * 45))

    def draw_shop(self):
        self.draw_ui_panel(f"DUNGEON MERCHANT - {self.player.gold} GOLD")
        from items.equipment import item_database
        y, buy_count = 175, len(self.shop_items)
        self.screen.blit(self.font_tiny.render("BUY (ENTER):", True, (100, 255, 100)), (120, y)); y += 25
        for i, skey in enumerate(self.shop_items):
            c = gold if i == self.shop_selection else white
            self.screen.blit(self.font_tiny.render(f"{item_database[skey].name.upper()} ({50 * self.current_stage}g)", True, c), (140, y)); y += 20
        y = 175
        self.screen.blit(self.font_tiny.render("SELL:", True, (255, 100, 100)), (400, y)); y += 25
        for i, item in enumerate(self.player.inventory.bag):
            c = gold if (i + buy_count) == self.shop_selection else white
            self.screen.blit(self.font_tiny.render(f"SELL {item.name.upper()} ({20 * self.current_stage}g)", True, c), (420, y)); y += 20

    def draw_forge(self):
        self.draw_ui_panel(f"THE FORGE - {self.player.forge_materials} SHARDS")
        self.screen.blit(self.font_tiny.render("UP/DOWN: select gear | ENTER: attempt upgrade | ESC: leave", True, (200, 200, 200)), (120, 145))
        
        forgeables = [i for i in self.player.inventory.bag if i.item_type == "equipment"]
        y = 180
        
        if not forgeables:
            self.screen.blit(self.font_tiny.render("no equipment in bag to upgrade.", True, white), (130, y))
            return
            
        visible_limit = 10
        for i in range(self.forge_scroll, min(len(forgeables), self.forge_scroll + visible_limit)):
            item = forgeables[i]
            color = white
            px = "  "
            if i == self.forge_selection:
                color = gold
                px = "> "
                
            cost = 1 + (item.upgrade_level * 2)
            chance = int(max(0.1, 1.0 - (item.upgrade_level * 0.08)) * 100)
            stat_str = f" [COST: {cost} shards | CHANCE: {chance}%]" if item.upgrade_level < 10 else " [MAX LEVEL]"
            
            self.screen.blit(self.font_tiny.render(f"{px}{item.name}{stat_str}", True, color), (130, y))
            y += 22

    def update(self):
        if self.state == state_exploration:
            now = pygame.time.get_ticks()
            if not hasattr(self, 'last_move'): self.last_move = now
            if now - self.last_move > 500:
                for e in self.enemies: e.map_wander(self.game_map, 64)
                self.last_move = now
                self.check_collisions()
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
            if self.menu_message:
                self.screen.blit(self.font_tiny.render(self.menu_message, True, (255, 100, 100)), (width//2 - 60, 250))
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
        elif self.state in [state_exploration, state_inventory, state_info, state_level_up, state_shop, "forge"]:
            self.game_map.draw(self.screen)
            self.exits.draw(self.screen)
            self.chests.draw(self.screen)
            self.forges.draw(self.screen)
            self.enemies.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            self.draw_hud()
            
            if self.state == state_inventory: self.draw_inventory()
            elif self.state == state_info: self.draw_info_screen()
            elif self.state == state_level_up: self.draw_level_up_screen()
            elif self.state == state_shop: self.draw_shop()
            elif self.state == "forge": self.draw_forge()
            
        elif self.state == state_combat:
            self.battle_system.draw()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(fps)
        pygame.quit()
        sys.exit()