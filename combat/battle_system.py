import pygame
import random
from settings import *
from items.equipment import item_database, get_random_loot

class BattleSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        self.player = None
        self.enemy = None
        self.panel_height = 150
        self.panel_y = height - self.panel_height
        self.menu_state = "main"
        self.options = ["attack", "magic", "items", "flee"]
        self.selected_option = 0
        self.magic_selected_option = 0
        self.item_selected_option = 0
        self.turn = "player"
        self.consecutive_turns = 1
        self.player_msg = ""
        self.enemy_msg = ""

    def start_battle(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.selected_option = 0
        self.magic_selected_option = 0
        self.item_selected_option = 0
        self.menu_state = "main"
        self.consecutive_turns = 1
        self.player_msg = ""
        self.enemy_msg = ""
        
        if self.enemy.speed > self.player.speed:
            self.turn = "enemy"
            self.enemy_msg = f"a wild {self.enemy.enemy_type} appears and outspeeds you!"
        else:
            self.turn = "player"
            self.player_msg = f"a wild {self.enemy.enemy_type} appears!"

    def advance_turn(self):
        if self.turn == "player":
            if self.enemy.current_health <= 0: return self.handle_victory()
            msgs = self.player.process_statuses()
            if msgs: self.player_msg += " " + " ".join(msgs)
            if self.player.current_health <= 0: return "defeat"
            
            if self.player.speed >= (self.enemy.speed * 2) and self.consecutive_turns < 2:
                self.consecutive_turns += 1
                self.player_msg += " (extra turn!)"
                self.turn = "player"
            else:
                self.consecutive_turns = 1
                self.turn = "enemy"
            return "continue"
            
        else:
            if self.player.current_health <= 0:
                self.enemy_msg += " you were defeated..."
                return "defeat"
            msgs = self.enemy.process_statuses()
            if msgs: self.enemy_msg += " " + " ".join(msgs)
            if self.enemy.current_health <= 0: return self.handle_victory()
            
            if self.enemy.speed >= (self.player.speed * 2) and self.consecutive_turns < 2:
                self.consecutive_turns += 1
                self.enemy_msg += " (extra turn!)"
                self.turn = "enemy"
            else:
                self.consecutive_turns = 1
                self.turn = "player"
            return "continue"

    def handle_victory(self):
        loot_key = get_random_loot(self.enemy.loot_table, self.enemy.stage)
        self.player.gold += self.enemy.gold
        self.player.forge_materials += self.enemy.forge_materials
        base_msg = f"victory! gained {self.enemy.gold}g"
        if self.enemy.forge_materials > 0: base_msg += f", {self.enemy.forge_materials} shards."
        else: base_msg += "."
            
        if loot_key:
            loot_item = item_database[loot_key]
            self.player.inventory.add_item(loot_item)
            self.player_msg = base_msg + f" found: {loot_item.original_name}!"
        else:
            self.player_msg = base_msg
        self.enemy_msg = ""
        return "victory"

    def execute_player_action(self):
        self.enemy_msg = ""
        is_stunned = "stun" in self.player.statuses
        damage_dealt = 0
        
        if is_stunned:
            self.player_msg = "you are stunned and cannot move!"
            return self.advance_turn()

        if self.menu_state == "main":
            if self.options[self.selected_option] == "attack":
                if random.random() < self.enemy.dodge_chance:
                    self.player_msg = f"{self.enemy.enemy_type} dodged your attack!"
                else:
                    base_damage = self.player.attack_damage
                    
                    # add a slight variance so attacks are not always identical
                    base_damage = int(base_damage * random.uniform(0.9, 1.1))
                    
                    berserk_power = self.player.has_skill("low_hp_buff")
                    if berserk_power > 0 and (self.player.current_health / self.player.max_health) < 0.3:
                        base_damage = int(base_damage * (1 + berserk_power))
                    is_crit = random.random() < self.player.crit_chance
                    if is_crit: base_damage = int(base_damage * self.player.crit_damage)
                        
                    damage_dealt = self.enemy.take_damage(base_damage, "physical")
                    msg_prefix = "critical hit! " if is_crit else ""
                    self.player_msg = f"{msg_prefix}dealt {damage_dealt} dmg."
                    
                    weapon = self.player.inventory.equipped.get("weapon")
                    if weapon and getattr(weapon, "element", None) and damage_dealt > 0:
                        elem = weapon.element
                        elem_dmg = getattr(weapon, "element_damage", 0)
                        if elem_dmg > 0:
                            self.enemy.take_damage(elem_dmg, "magic")
                            damage_dealt += elem_dmg
                            self.player_msg += f" +{elem_dmg} {elem} dmg!"
                        if random.random() < 0.30:
                            if elem == "fire":
                                self.enemy.apply_status("burn", 3, max(1, damage_dealt // 4))
                                self.player_msg += " enemy burning!"
                            elif elem == "ice":
                                self.enemy.apply_status("stun", 1, 0)
                                self.player_msg += " enemy frozen!"
                            elif elem == "poison":
                                self.enemy.apply_status("poison", 3, max(1, damage_dealt // 5))
                                self.player_msg += " enemy poisoned!"
                            elif elem == "lightning":
                                self.enemy.apply_status("shock", 2, max(1, damage_dealt // 3))
                                self.player_msg += " enemy shocked!"
                        
            elif self.options[self.selected_option] == "magic":
                if not self.player.spells:
                    self.player_msg = "you know no spells!"
                    return "continue"
                self.menu_state = "magic"
                self.magic_selected_option = 0
                return "continue"
                
            elif self.options[self.selected_option] == "items":
                consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
                if not consumables:
                    self.player_msg = "you have no items!"
                    return "continue"
                self.menu_state = "items"
                self.item_selected_option = 0
                return "continue"
                
            elif self.options[self.selected_option] == "flee":
                if self.player.speed > self.enemy.speed:
                    self.player_msg = "successfully escaped combat!"
                    return "flee_success"
                else:
                    self.player_msg = "escape unsuccessful!"
                    return self.advance_turn()
                    
        elif self.menu_state == "magic":
            if self.magic_selected_option == len(self.player.spells):
                self.menu_state = "main"
                return "continue"
            spell = self.player.spells[self.magic_selected_option]
            success, msg = spell.cast(self.player, self.enemy)
            self.player_msg = msg
            self.menu_state = "main"
            if not success: return "continue"
            
        elif self.menu_state == "items":
            consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
            if self.item_selected_option == len(consumables):
                self.menu_state = "main"
                return "continue"
            item = consumables[self.item_selected_option]
            success, msg = item.use(self.player)
            self.player_msg = msg
            self.menu_state = "main"
            if success: self.player.inventory.remove_item(item)
            else: return "continue"

        vamp_power = self.player.has_skill("life_steal")
        if vamp_power > 0 and damage_dealt > 0:
            heal_amt = int(damage_dealt * vamp_power)
            self.player.current_health = min(self.player.max_health, self.player.current_health + heal_amt)
        m_regen = self.player.has_skill("mana_regen")
        if m_regen > 0:
            self.player.current_mana = min(self.player.max_mana, self.player.current_mana + m_regen)

        return self.advance_turn()

    def execute_enemy_turn(self):
        is_stunned = "stun" in self.enemy.statuses
        if is_stunned:
            self.enemy_msg = f"{self.enemy.enemy_type} is stunned and cannot move!"
            return self.advance_turn()
            
        dodge_roll = random.random()
        cheat_death_power = self.player.has_skill("cheat_death")
        if dodge_roll < self.player.dodge_chance or dodge_roll < cheat_death_power:
            self.enemy_msg = "you dodged the attack!"
        else:
            base_damage = self.enemy.attack_damage
            
            # difficulty fix: scale enemy damage so it pierces flat armor in late game stages
            base_damage = int(base_damage * random.uniform(0.9, 1.1))
            
            # add a 15 percent chance for the enemy to land a critical hit
            is_crit = random.random() < 0.15
            if is_crit:
                base_damage = int(base_damage * 1.5)
                
            # anti-armor measure: enemies always deal at least 5 percent of your max health plus stage level
            # this ensures that even if you have massive defense, you are constantly pressured
            armor_pierce = int(self.player.max_health * 0.05) + self.enemy.stage
            base_damage += armor_pierce
            
            damage_dealt = self.player.take_damage(base_damage, "physical")
            
            crit_msg = "CRITICAL HIT! " if is_crit else ""
            self.enemy_msg = f"{crit_msg}{self.enemy.enemy_type} hits you for {damage_dealt} damage!"
            
        return self.advance_turn()

    def draw_text_wrapped(self, text, color, start_x, start_y, max_width):
        words = text.split(' ')
        lines = []
        curr_line = ""
        for word in words:
            if self.font.size(curr_line + word)[0] < max_width:
                curr_line += word + " "
            else:
                lines.append(curr_line)
                curr_line = word + " "
        lines.append(curr_line)
        for i, line in enumerate(lines):
            self.screen.blit(self.font.render(line, True, color), (start_x, start_y + i * 25))
        return len(lines) * 25

    def draw(self):
        self.screen.fill((20, 20, 30))
        if not self.player or not self.enemy: return
            
        p_offset = self.draw_text_wrapped(self.player_msg, white, 40, 40, width - 100)
        self.draw_text_wrapped(self.enemy_msg, (255, 100, 100), 40, 40 + p_offset, width - 100)
            
        enemy_rect = self.enemy.image.get_rect(center=(width // 2, height // 3))
        self.screen.blit(self.enemy.image, enemy_rect)
        
        enemy_text = self.font.render(f"{self.enemy.enemy_type.upper()} STAGE {self.enemy.stage}", True, white)
        enemy_hp_text = self.font.render(f"HP: {self.enemy.current_health}/{self.enemy.max_health}", True, (255, 100, 100))
        self.screen.blit(enemy_text, (enemy_rect.x, enemy_rect.y - 60))
        self.screen.blit(enemy_hp_text, (enemy_rect.x, enemy_rect.y - 30))
        
        status_y = enemy_rect.y - 90
        for status, data in self.enemy.statuses.items():
            s_text = self.font.render(f"{status.upper()} ({data['duration']}T)", True, (200, 50, 200))
            self.screen.blit(s_text, (enemy_rect.x, status_y))
            status_y -= 30

        pygame.draw.rect(self.screen, black, (0, self.panel_y, width, self.panel_height))
        pygame.draw.rect(self.screen, white, (0, self.panel_y, width, self.panel_height), 2)
        
        p_name = self.font.render(f"{self.player.name.upper()} LVL {self.player.level}", True, gold)
        p_hp = self.font.render(f"HP: {self.player.current_health}/{self.player.max_health}", True, (100, 255, 100))
        p_mp = self.font.render(f"MP: {self.player.current_mana}/{self.player.max_mana}", True, (100, 100, 255))
        
        self.screen.blit(p_name, (40, self.panel_y + 20))
        self.screen.blit(p_hp, (40, self.panel_y + 55))
        self.screen.blit(p_mp, (40, self.panel_y + 90))

        p_status_y = self.panel_y - 30
        for status, data in self.player.statuses.items():
            s_text = self.font.render(f"{status.upper()} ({data['duration']}T)", True, (200, 50, 200))
            self.screen.blit(s_text, (40, p_status_y))
            p_status_y -= 30
        
        menu_x = width - 400
        if self.menu_state == "main":
            for i, option in enumerate(self.options):
                color = gold if i == self.selected_option else white
                txt = self.font.render(option.upper(), True, color)
                self.screen.blit(txt, (menu_x, self.panel_y + 15 + (i * 32)))
        elif self.menu_state == "magic":
            for i, spell in enumerate(self.player.spells):
                color = gold if i == self.magic_selected_option else white
                txt = self.font.render(f"{spell.name.upper()} LVL {spell.level} ({spell.mana_cost}MP)", True, color)
                self.screen.blit(txt, (menu_x, self.panel_y + 15 + (i * 30)))
            back_idx = len(self.player.spells)
            color = gold if back_idx == self.magic_selected_option else white
            txt = self.font.render("BACK", True, color)
            self.screen.blit(txt, (menu_x, self.panel_y + 15 + (back_idx * 30)))
        elif self.menu_state == "items":
            consumables = [i for i in self.player.inventory.bag if i.item_type == "consumable"]
            for i, item in enumerate(consumables):
                color = gold if i == self.item_selected_option else white
                qty_str = f" (x{item.quantity})" if hasattr(item, 'quantity') and item.quantity > 1 else ""
                txt = self.font.render(f"{item.name.upper()}{qty_str}", True, color)
                self.screen.blit(txt, (menu_x, self.panel_y + 15 + (i * 30)))
            back_idx = len(consumables)
            color = gold if back_idx == self.item_selected_option else white
            txt = self.font.render("BACK", True, color)
            self.screen.blit(txt, (menu_x, self.panel_y + 15 + (back_idx * 30)))