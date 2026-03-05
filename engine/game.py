import pygame
import sys
from settings import *
from world.map import Map
from entities.player import Player
from entities.enemy import Enemy
from combat.battle_system import BattleSystem

class Game:
    def __init__(self):
        # initialize basic display setup
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("retro rpg")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # set initial game state
        self.state = state_exploration
        
        # initialize game world
        self.game_map = Map()
        
        # setup player at tile coordinate 1, 1
        start_x = 1 * self.game_map.tile_size
        start_y = 1 * self.game_map.tile_size
        self.player = Player(start_x, start_y, "hero", "warrior")
        
        # initialize battle system
        self.battle_system = BattleSystem(self.screen)
        
        # setup enemy group
        self.enemies = pygame.sprite.Group()
        self.spawn_enemies()

    def spawn_enemies(self):
        # find all walkable tiles on the map
        valid_tiles = []
        for row_index, row in enumerate(self.game_map.grid):
            for col_index, tile in enumerate(row):
                if tile == 0:
                    valid_tiles.append((col_index, row_index))
                    
        # randomly select a valid floor tile for the slime
        if valid_tiles:
            import random
            spawn_col, spawn_row = random.choice(valid_tiles)
            
            slime_x = spawn_col * self.game_map.tile_size
            slime_y = spawn_row * self.game_map.tile_size
            slime = Enemy(slime_x, slime_y, "jelly", "slime", level=1)
            self.enemies.add(slime)

    def handle_events(self):
        # process user inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # route inputs based on current state
            if self.state == state_exploration:
                if event.type == pygame.KEYDOWN:
                    self.handle_exploration_input(event.key)
            elif self.state == state_combat:
                if event.type == pygame.KEYDOWN:
                    self.handle_combat_input(event.key)
            elif self.state == state_inventory:
                if event.type == pygame.KEYDOWN:
                    self.handle_inventory_input(event.key)

    def handle_exploration_input(self, key):
        # existing movement logic...
        next_x = self.player.rect.x
        next_y = self.player.rect.y
        step = self.game_map.tile_size
        
        if key == pygame.K_LEFT or key == pygame.K_a:
            next_x -= step
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            next_x += step
        elif key == pygame.K_UP or key == pygame.K_w:
            next_y -= step
        elif key == pygame.K_DOWN or key == pygame.K_s:
            next_y += step
        elif key == pygame.K_i:
            # open inventory screen
            self.state = state_inventory
            return
            
        # check map collision before finalizing movement
        if self.game_map.is_walkable(next_x, next_y):
            self.player.rect.x = next_x
            self.player.rect.y = next_y
            self.check_enemy_collisions()

    def handle_inventory_input(self, key):
        # press i or escape to close the menu
        if key == pygame.K_i or key == pygame.K_ESCAPE:
            self.state = state_exploration
        # press a to automatically equip the best gear
        elif key == pygame.K_a:
            self.player.inventory.auto_equip(self.player)

    def handle_combat_input(self, key):
        # capture input during the battle phase
        if self.battle_system.turn == "player":
            
            # allow backing out of the magic menu
            if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
                if self.battle_system.menu_state == "magic":
                    self.battle_system.menu_state = "main"
                    return

            # navigate up the menu
            if key == pygame.K_UP or key == pygame.K_w:
                if self.battle_system.menu_state == "main":
                    self.battle_system.selected_option -= 1
                    if self.battle_system.selected_option < 0:
                        self.battle_system.selected_option = len(self.battle_system.options) - 1
                elif self.battle_system.menu_state == "magic":
                    self.battle_system.magic_selected_option -= 1
                    if self.battle_system.magic_selected_option < 0:
                        self.battle_system.magic_selected_option = len(self.battle_system.player.spells) - 1
            
            # navigate down the menu
            elif key == pygame.K_DOWN or key == pygame.K_s:
                if self.battle_system.menu_state == "main":
                    self.battle_system.selected_option += 1
                    if self.battle_system.selected_option >= len(self.battle_system.options):
                        self.battle_system.selected_option = 0
                elif self.battle_system.menu_state == "magic":
                    self.battle_system.magic_selected_option += 1
                    if self.battle_system.magic_selected_option >= len(self.battle_system.player.spells):
                        self.battle_system.magic_selected_option = 0
            
            # confirm selection
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                result = self.battle_system.execute_player_action()
                self.process_battle_result(result)
                
        elif self.battle_system.turn == "enemy":
            # force player to press enter to advance the text and trigger enemy turn
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                result = self.battle_system.execute_enemy_turn()
                self.process_battle_result(result)

    def process_battle_result(self, result):
        # handle state changes based on combat outcome
        if result == "flee":
            self.state = state_exploration
        elif result == "victory":
            self.state = state_exploration
            # remove the defeated enemy from the map
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hit_enemies:
                hit_enemies[0].die()
        elif result == "defeat":
            print("you died. game over.")
            self.running = False

    def check_enemy_collisions(self):
        # check if player bumped into any enemy in the group
        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hit_enemies:
            print(f"encountered a {hit_enemies[0].enemy_type}!")
            
            # pass combatants to the battle system
            self.battle_system.start_battle(self.player, hit_enemies[0])
            
            # switch the game state to combat
            self.state = state_combat

    def update(self):
        # process continuous background logic only during exploration
        if self.state == state_exploration:
            
            # grab the current time in milliseconds
            current_time = pygame.time.get_ticks()
            
            # initialize the timer attribute if it does not exist yet
            if not hasattr(self, 'last_enemy_move'):
                self.last_enemy_move = current_time
                
            # trigger enemy movement every 500 milliseconds
            if current_time - self.last_enemy_move > 500:
                for enemy in self.enemies:
                    # pass the map and the tile size to handle grid math
                    enemy.map_wander(self.game_map, self.game_map.tile_size)
                    
                # reset the timer after they move
                self.last_enemy_move = current_time
                
                # check if an enemy walked directly into the player
                self.check_enemy_collisions()

    def draw_inventory(self):
        font = pygame.font.Font(None, 32)
        
        # draw a semi transparent dark overlay over the map
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(200)
        overlay.fill(black)
        self.screen.blit(overlay, (0, 0))
        
        # draw title and instructions
        title = font.render("character gear & inventory", True, white)
        instructions = font.render("press 'A' to auto-equip | press 'I' to close", True, (200, 200, 200))
        self.screen.blit(title, (40, 40))
        self.screen.blit(instructions, (40, 80))
        
        # draw equipped gear column
        pygame.draw.rect(self.screen, white, (40, 130, 300, 400), 2)
        equip_title = font.render("equipped slots", True, (100, 255, 100))
        self.screen.blit(equip_title, (60, 150))
        
        y_offset = 200
        for slot, item in self.player.inventory.equipped.items():
            item_name = item.name if item else "empty"
            text = font.render(f"{slot.capitalize()}: {item_name}", True, white)
            self.screen.blit(text, (60, y_offset))
            y_offset += 50
            
        # draw bag contents column
        pygame.draw.rect(self.screen, white, (360, 130, 400, 400), 2)
        bag_title = font.render("items in bag", True, (100, 100, 255))
        self.screen.blit(bag_title, (380, 150))
        
        y_offset = 200
        if not self.player.inventory.bag:
            empty_text = font.render("bag is empty.", True, (150, 150, 150))
            self.screen.blit(empty_text, (380, y_offset))
        else:
            for item in self.player.inventory.bag:
                text = font.render(f"- {item.name} ({item.item_type})", True, white)
                self.screen.blit(text, (380, y_offset))
                y_offset += 30

    def draw(self):
        # clear the screen
        self.screen.fill(dark_grey)
        
        # render graphics based on current state
        if self.state == state_exploration:
            self.game_map.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect)
                
        elif self.state == state_combat:
            # hand over rendering control to the battle system
            self.battle_system.draw()
            
        elif self.state == state_inventory:
            # draw the map in the background, then layer the inventory on top
            self.game_map.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            self.draw_inventory()
            
        pygame.display.flip()

    def run(self):
        # main engine loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(fps)
            
        pygame.quit()
        sys.exit()