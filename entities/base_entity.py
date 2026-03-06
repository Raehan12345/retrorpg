import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.name = name
        self.image = pygame.Surface((64, 64))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.max_health = 100
        self.current_health = 100
        self.max_mana = 50
        self.current_mana = 50
        self.attack_damage = 10
        self.magic_damage = 10
        self.armor = 5
        self.speed = 5
        self.crit_chance = 0.05
        self.crit_damage = 1.5
        self.dodge_chance = 0.05
        
        self.gold = 0
        self.statuses = {}

    def take_damage(self, amount, damage_type="physical"):
        mitigation = self.armor if damage_type == "physical" else 0
        final_damage = max(1, amount - mitigation)
        self.current_health -= final_damage
        return final_damage

    def apply_status(self, status_name, duration, power=0):
        self.statuses[status_name] = {"duration": duration, "power": power}

    def process_statuses(self):
        messages = []
        keys_to_remove = []
        
        for status, data in self.statuses.items():
            if status in ["poison", "bleed", "burn"]:
                dmg = max(1, data["power"])
                self.current_health -= dmg
                messages.append(f"{self.name} took {dmg} {status} damage.")
            elif status == "shock":
                dmg = max(1, data["power"] + 2)
                self.current_health -= dmg
                messages.append(f"{self.name} shocked for {dmg} damage.")
                
            data["duration"] -= 1
            if data["duration"] <= 0:
                keys_to_remove.append(status)
                
        for key in keys_to_remove:
            del self.statuses[key]
            messages.append(f"{self.name} recovered from {key}.")
            
        return messages