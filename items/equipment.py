class Item:
    def __init__(self, name, item_type, description, rarity="common"):
        # base properties for any item
        self.name = name
        self.item_type = item_type
        self.description = description
        self.rarity = rarity

class Consumable(Item):
    def __init__(self, name, description, rarity, effect_type, amount):
        # initialize parent class
        super().__init__(name, "consumable", description, rarity)
        self.effect_type = effect_type
        self.amount = amount

    def use(self, target):
        # apply specific consumable effects
        if self.effect_type == "heal":
            target.current_health = min(target.max_health, target.current_health + self.amount)
            return True, f"healed for {self.amount} hp."
        elif self.effect_type == "mana":
            target.current_mana = min(target.max_mana, target.current_mana + self.amount)
            return True, f"restored {self.amount} mp."
            
        return False, "nothing happened."

class Equipment(Item):
    def __init__(self, name, slot, description, rarity, base_stats):
        # initialize parent class
        super().__init__(name, "equipment", description, rarity)
        self.slot = slot
        self.base_stats = base_stats
        self.stats = {}
        
        # apply rarity multipliers
        self.apply_rarity_scaling()

    def apply_rarity_scaling(self):
        # define multiplier based on rarity tier
        multipliers = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0
        }
        
        # fallback to standard multiplier if rarity is not found
        multiplier = multipliers.get(self.rarity, 1.0)
        
        # calculate final stats based on base stats and multiplier
        for stat, value in self.base_stats.items():
            # we use int to avoid floating point health or damage values
            self.stats[stat] = int(value * multiplier)

# dictionary holding available items in the game
item_database = {
    # consumables
    "minor health potion": Consumable("minor health potion", "restores 25 hp.", "common", "heal", 25),
    "minor mana potion": Consumable("minor mana potion", "restores 20 mp.", "common", "mana", 20),
    
    # weapons
    "iron sword": Equipment("iron sword", "weapon", "a basic iron blade.", "common", {"attack_damage": 5}),
    "apprentice staff": Equipment("apprentice staff", "weapon", "a simple wooden staff.", "common", {"magic_damage": 5, "max_mana": 10}),
    "obsidian dagger": Equipment("obsidian dagger", "weapon", "a razor sharp glass dagger.", "rare", {"attack_damage": 6, "crit_chance": 0.05, "speed": 2}),
    
    # armor
    "leather tunic": Equipment("leather tunic", "armor", "provides basic protection.", "common", {"armor": 3}),
    "wizard robe": Equipment("wizard robe", "armor", "infused with minor magic.", "common", {"armor": 1, "max_mana": 20}),
    
    # accessories
    "ruby ring": Equipment("ruby ring", "ring", "glows faintly.", "uncommon", {"max_health": 20}),
    "sapphire necklace": Equipment("sapphire necklace", "necklace", "cool to the touch.", "rare", {"max_mana": 30, "magic_damage": 5})
}