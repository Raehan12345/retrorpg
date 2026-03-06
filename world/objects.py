import pygame
from items.equipment import item_database, get_random_loot

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y, stage=1):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 150, 50))
        self.rect = self.image.get_rect(topleft=(x + 16, y + 16))
        self.stage = stage
        # added elemental items to the standard chest pool
        self.loot_table = [("ruby ring", 15), ("sapphire necklace", 15), ("broadsword", 20), ("hunter tunic", 20), ("longbow", 15), ("venom spear", 10), ("flame sword", 10), ("frost dagger", 10), ("storm bow", 5)]

    def open(self, player):
        loot_key = get_random_loot(self.loot_table, self.stage)
        if loot_key:
            item = item_database[loot_key]
            player.inventory.add_item(item)
            return f"opened chest: found {item.original_name}!"
        return "the chest was empty."

class ExitPortal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((48, 48))
        self.image.fill((100, 50, 200))
        self.rect = self.image.get_rect(topleft=(x + 8, y + 8))

class Forge(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((100, 100, 150))
        self.rect = self.image.get_rect(topleft=(x + 12, y + 12))