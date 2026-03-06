import random

class Item:
    def __init__(self, name, item_type, description, rarity="common"):
        self.original_name = name
        self.name = name
        self.item_type = item_type
        self.description = description
        self.rarity = rarity
        self.quantity = 1

class Consumable(Item):
    def __init__(self, name, description, rarity, effect_type, amount):
        super().__init__(name, "consumable", description, rarity)
        self.effect_type = effect_type
        self.amount = amount

    def use(self, target):
        if self.effect_type == "heal":
            target.current_health = min(target.max_health, target.current_health + self.amount)
            return True, f"healed for {self.amount} hp."
        elif self.effect_type == "mana":
            target.current_mana = min(target.max_mana, target.current_mana + self.amount)
            return True, f"restored {self.amount} mp."
        return False, "nothing happened."

class Equipment(Item):
    def __init__(self, name, slot, description, rarity, base_stats, element=None, element_damage=0):
        super().__init__(name, "equipment", description, rarity)
        self.slot = slot
        self.base_stats = base_stats
        self.stats = {}
        self.element = element
        self.element_damage = element_damage
        self.upgrade_level = 0
        self.apply_rarity_scaling()
        self.update_name()

    def update_name(self):
        prefix = f"[{self.element.upper()}] " if self.element else ""
        suffix = f" +{self.upgrade_level}" if self.upgrade_level > 0 else ""
        self.name = f"{prefix}{self.original_name}{suffix}"

    def upgrade(self):
        if self.upgrade_level < 10:
            self.upgrade_level += 1
            for stat, val in self.base_stats.items():
                bonus = max(1, int(val * 0.10))
                self.stats[stat] += bonus
            if self.element_damage > 0: self.element_damage += 2
            self.update_name()
            return True
        return False

    def apply_rarity_scaling(self):
        multipliers = {"common": 1.0, "uncommon": 1.2, "rare": 1.5, "epic": 2.0, "legendary": 3.0}
        multiplier = multipliers.get(self.rarity, 1.0)
        for stat, value in self.base_stats.items():
            self.stats[stat] = int(value * multiplier)

item_database = {
    "minor health potion": Consumable("minor health potion", "restores 25 hp.", "common", "heal", 25),
    "major health potion": Consumable("major health potion", "restores 75 hp.", "rare", "heal", 75),
    "minor mana potion": Consumable("minor mana potion", "restores 20 mp.", "common", "mana", 20),
    "major mana potion": Consumable("major mana potion", "restores 60 mp.", "rare", "mana", 60),
    
    "iron sword": Equipment("iron sword", "weapon", "basic iron blade.", "common", {"attack_damage": 5}),
    "broadsword": Equipment("broadsword", "weapon", "wide and heavy.", "uncommon", {"attack_damage": 11}),
    "steel claymore": Equipment("steel claymore", "weapon", "heavy two-handed sword.", "uncommon", {"attack_damage": 12, "speed": -1}),
    "flame sword": Equipment("flame sword", "weapon", "a blade of pure fire.", "rare", {"attack_damage": 15}, element="fire", element_damage=5),
    "dragon slayer": Equipment("dragon slayer", "weapon", "legendary massive blade.", "legendary", {"attack_damage": 40, "armor": 5}),
    
    "obsidian dagger": Equipment("obsidian dagger", "weapon", "razor sharp glass.", "rare", {"attack_damage": 8, "crit_chance": 0.10}),
    "frost dagger": Equipment("frost dagger", "weapon", "chills to the bone.", "uncommon", {"attack_damage": 10, "crit_chance": 0.05}, element="ice", element_damage=3),
    "shadow fang": Equipment("shadow fang", "weapon", "dagger of the abyss.", "epic", {"attack_damage": 15, "speed": 3, "crit_chance": 0.15}, element="poison", element_damage=6),
    
    "shortbow": Equipment("shortbow", "weapon", "a simple hunting bow.", "common", {"attack_damage": 6, "speed": 2}),
    "longbow": Equipment("longbow", "weapon", "a sturdy war bow.", "uncommon", {"attack_damage": 14, "speed": 1}),
    "venom spear": Equipment("venom spear", "weapon", "dripping with acid.", "rare", {"attack_damage": 14}, element="poison", element_damage=4),
    "storm bow": Equipment("storm bow", "weapon", "crackles with thunder.", "epic", {"attack_damage": 18, "speed": 4}, element="lightning", element_damage=8),
    
    "apprentice staff": Equipment("apprentice staff", "weapon", "simple wooden staff.", "common", {"magic_damage": 5, "max_mana": 10}),
    "sage wand": Equipment("sage wand", "weapon", "channeled magic focus.", "uncommon", {"magic_damage": 12}),
    "archmage scepter": Equipment("archmage scepter", "weapon", "overflowing with power.", "epic", {"magic_damage": 25, "max_mana": 50}),
    
    "leather tunic": Equipment("leather tunic", "armor", "basic protection.", "common", {"armor": 3}),
    "hunter tunic": Equipment("hunter tunic", "armor", "light and flexible.", "uncommon", {"armor": 5, "speed": 1}),
    "chainmail": Equipment("chainmail", "armor", "sturdy metal links.", "uncommon", {"armor": 8, "speed": -1}),
    "mithril mail": Equipment("mithril mail", "armor", "lightweight but strong.", "rare", {"armor": 12, "speed": 1}),
    "plate armor": Equipment("plate armor", "armor", "heavy knight armor.", "rare", {"armor": 15, "speed": -2}),
    "wizard robe": Equipment("wizard robe", "armor", "magic infused silk.", "common", {"armor": 1, "max_mana": 20}),
    "shadow cloak": Equipment("shadow cloak", "armor", "blends into the dark.", "epic", {"armor": 8, "dodge_chance": 0.10}),
    "elder cloak": Equipment("elder cloak", "armor", "ancient protective garb.", "rare", {"armor": 5, "magic_damage": 10}),
    
    "topaz ring": Equipment("topaz ring", "ring", "boosts energy.", "common", {"max_mana": 15}),
    "ruby ring": Equipment("ruby ring", "ring", "boosts vitality.", "uncommon", {"max_health": 20}),
    "emerald band": Equipment("emerald band", "ring", "boosts agility.", "uncommon", {"speed": 2}),
    "obsidian band": Equipment("obsidian band", "ring", "hard as rock.", "rare", {"armor": 4, "attack_damage": 5}),
    "sapphire necklace": Equipment("sapphire necklace", "necklace", "magic focus.", "rare", {"max_mana": 30, "magic_damage": 5}),
    "pendant of life": Equipment("pendant of life", "necklace", "massive hp boost.", "epic", {"max_health": 100})
}

def get_random_loot(table, stage=1):
    boss_kills = stage // 5
    adjusted_table = []
    for item_key, weight in table:
        if item_key is not None:
            new_weight = int(weight * (1 + (0.2 * boss_kills)))
            adjusted_table.append((item_key, new_weight))
        else:
            new_weight = max(5, int(weight * (1 - (0.1 * boss_kills))))
            adjusted_table.append((item_key, new_weight))
            
    total_weight = sum(w for i, w in adjusted_table)
    roll = random.randint(1, total_weight)
    
    current = 0
    for item_key, weight in adjusted_table:
        current += weight
        if roll <= current: return item_key
    return None