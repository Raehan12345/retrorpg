width = 800
height = 600
fps = 60
tile_size = 64

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gold = (255, 215, 0)

# Game States
state_main_menu = "main_menu"
state_naming = "naming"
state_class_select = "class_select"
state_exploration = "exploration"
state_combat = "combat"
state_inventory = "inventory"
state_level_up = "level_up"
state_info = "info"
state_shop = "shop"

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)