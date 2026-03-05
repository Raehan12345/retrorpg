import pygame
import random
from settings import *

class BattleSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # combat participants
        self.player = None
        self.enemy = None
        
        # ui panel dimensions
        self.panel_height = 150
        self.panel_y = height - self.panel_height
        
        # menu states and options
        self.menu_state = "main"
        self.options = ["attack", "magic", "flee"]
        self.selected_option = 0
        self.magic_selected_option = 0
        
        # battle state tracking
        self.turn = "player"
        self.battle_message = ""

    def start_battle(self, player, enemy):
        # lock in the combatants when a fight triggers
        self.player = player
        self.enemy = enemy
        self.selected_option = 0
        self.magic_selected_option = 0
        self.menu_state = "main"
        self.turn = "player"
        self.battle_message = f"a wild {self.enemy.enemy_type} appears!"

    def execute_player_action(self):
        # route logic based on current menu state
        if self.menu_state == "main":
            if self.options[self.selected_option] == "attack":
                
                # check if the enemy dodges completely
                if random.random() < self.enemy.dodge_chance:
                    self.battle_message = f"the {self.enemy.enemy_type} dodged your attack!"
                else:
                    # set up base damage and roll for a critical hit
                    base_damage = self.player.attack_damage
                    is_crit = random.random() < self.player.crit_chance
                    
                    if is_crit:
                        # apply critical damage multiplier
                        base_damage = int(base_damage * self.player.crit_damage)
                        
                    # execute damage reduction logic
                    start_hp = self.enemy.current_health
                    self.enemy.take_damage(base_damage, "physical")
                    damage_dealt = start_hp - self.enemy.current_health
                    
                    # output correct visual feedback
                    if is_crit:
                        self.battle_message = f"critical hit! you dealt {damage_dealt} damage!"
                    else:
                        self.battle_message = f"you dealt {damage_dealt} damage!"
                        
            elif self.options[self.selected_option] == "magic":
                # switch to magic menu if player has spells
                if not self.player.spells:
                    self.battle_message = "you know no abilities!"
                    return "continue"
                    
                self.menu_state = "magic"
                self.magic_selected_option = 0
                return "continue"
                
            elif self.options[self.selected_option] == "flee":
                self.battle_message = "you attempt to run away..."
                return "flee"
                
        elif self.menu_state == "magic":
            # fetch the selected spell
            spell = self.player.spells[self.magic_selected_option]
            
            # attempt to cast
            success, msg = spell.cast(self.player, self.enemy)
            self.battle_message = msg
            
            if not success:
                # failed to cast due to mana, return to main menu
                self.menu_state = "main"
                return "continue"
                
            # cast successful, return to main menu for next turn
            self.menu_state = "main"
            
        # check if enemy died from the attack or spell
        if self.enemy.current_health <= 0:
            self.battle_message = f"you defeated the {self.enemy.enemy_type}!"
            self.player.gain_experience(self.enemy.exp_reward)
            return "victory"
            
        # hand the turn over to the enemy
        self.turn = "enemy"
        return "continue"

    def execute_enemy_turn(self):
        # check if the player dodges
        if random.random() < self.player.dodge_chance:
            self.battle_message = "you dodged the attack!"
        else:
            # set up base damage and roll for critical hit
            base_damage = self.enemy.attack_damage
            is_crit = random.random() < self.enemy.crit_chance
            
            if is_crit:
                base_damage = int(base_damage * self.enemy.crit_damage)
                
            # execute damage reduction logic
            start_hp = self.player.current_health
            self.player.take_damage(base_damage, "physical")
            damage_dealt = start_hp - self.player.current_health
            
            # output correct visual feedback
            if is_crit:
                self.battle_message = f"critical hit! {self.enemy.enemy_type} dealt {damage_dealt} damage!"
            else:
                self.battle_message = f"the {self.enemy.enemy_type} hit you for {damage_dealt} damage!"
        
        # check if player died
        if self.player.current_health <= 0:
            self.battle_message = "you have been defeated..."
            return "defeat"
            
        # pass turn back to player
        self.turn = "player"
        return "continue"

    def draw(self):
        # fill background with a dark void for the battle screen
        self.screen.fill((20, 20, 30))
        
        if not self.player or not self.enemy:
            return
            
        # draw battle message at the top left
        message_text = self.font.render(self.battle_message, True, white)
        self.screen.blit(message_text, (40, 40))
            
        # draw enemy sprite in the center
        enemy_rect = self.enemy.image.get_rect(center=(width // 2, height // 3))
        self.screen.blit(self.enemy.image, enemy_rect)
        
        # draw enemy name and health above them
        enemy_text = self.font.render(f"{self.enemy.enemy_type} lvl {self.enemy.level}", True, white)
        enemy_hp_text = self.font.render(f"hp: {self.enemy.current_health}/{self.enemy.max_health}", True, (255, 100, 100))
        self.screen.blit(enemy_text, (enemy_rect.x, enemy_rect.y - 60))
        self.screen.blit(enemy_hp_text, (enemy_rect.x, enemy_rect.y - 30))
        
        # draw bottom ui panel background
        pygame.draw.rect(self.screen, black, (0, self.panel_y, width, self.panel_height))
        pygame.draw.rect(self.screen, white, (0, self.panel_y, width, self.panel_height), 2)
        
        # draw player stats on the left side of the panel
        player_text = self.font.render(self.player.name.upper(), True, white)
        hp_text = self.font.render(f"hp: {self.player.current_health}/{self.player.max_health}", True, (100, 255, 100))
        mp_text = self.font.render(f"mp: {self.player.current_mana}/{self.player.max_mana}", True, (100, 100, 255))
        
        self.screen.blit(player_text, (40, self.panel_y + 20))
        self.screen.blit(hp_text, (40, self.panel_y + 60))
        self.screen.blit(mp_text, (40, self.panel_y + 100))
        
        # draw command menu on the right side of the panel
        menu_start_x = width - 300
        
        if self.menu_state == "main":
            for i, option in enumerate(self.options):
                # highlight the currently selected option
                color = (255, 255, 100) if i == self.selected_option else white
                option_text = self.font.render(option.upper(), True, color)
                self.screen.blit(option_text, (menu_start_x, self.panel_y + 20 + (i * 40)))
        elif self.menu_state == "magic":
            for i, spell in enumerate(self.player.spells):
                # highlight the currently selected spell
                color = (255, 255, 100) if i == self.magic_selected_option else white
                
                # display spell name and mana cost
                spell_display = f"{spell.name.upper()} ({spell.mana_cost} MP)"
                spell_text = self.font.render(spell_display, True, color)
                self.screen.blit(spell_text, (menu_start_x, self.panel_y + 20 + (i * 40)))