import copy

class Spell:
    def __init__(self, name, mana_cost, damage_type, base_power, description, status_effect=None, status_duration=0):
        self.name = name
        self.mana_cost = mana_cost
        self.damage_type = damage_type
        self.base_power = base_power
        self.description = description
        self.level = 1
        self.max_level = 5
        self.status_effect = status_effect
        self.status_duration = status_duration

    def get_current_power(self):
        # scale power based on current level
        return self.base_power + int(self.base_power * 0.3 * (self.level - 1))

    def cast(self, caster, target):
        if caster.current_mana < self.mana_cost:
            return False, "not enough mana!"
            
        caster.current_mana -= self.mana_cost
        power = self.get_current_power()
        
        if self.damage_type == "physical":
            total_damage = power + caster.attack_damage
        elif self.damage_type == "magic":
            total_damage = power + caster.magic_damage
        else:
            total_damage = power
            
        start_hp = target.current_health
        target.take_damage(total_damage, self.damage_type)
        actual_damage = start_hp - target.current_health
        
        msg = f"used {self.name} lvl {self.level}! dealt {actual_damage} damage."
        
        if self.status_effect:
            status_power = max(1, int(power * 0.2))
            target.apply_status(self.status_effect, self.status_duration, status_power)
            msg += f" applied {self.status_effect}!"
        
        return True, msg

spell_database = {
    # warrior
    "heavy strike": Spell("heavy strike", 15, "physical", 20, "a powerful physical blow.", "stun", 1),
    "shield bash": Spell("shield bash", 10, "physical", 10, "bashes the enemy with a shield.", "stun", 1),
    "rend": Spell("rend", 12, "physical", 15, "tears the enemy causing bleeding.", "bleed", 3),
    "warcry": Spell("warcry", 20, "magic", 5, "intimidates the enemy.", "stun", 2),
    
    # mage
    "fireball": Spell("fireball", 20, "magic", 35, "hurls a blazing fireball.", "burn", 2),
    "ice shard": Spell("ice shard", 15, "magic", 25, "shoots a piercing shard of ice.", "stun", 1),
    "lightning bolt": Spell("lightning bolt", 25, "magic", 40, "high damage lightning strike.", "shock", 2),
    "venom blast": Spell("venom blast", 18, "magic", 20, "toxic magic attack.", "poison", 4),
    
    # rogue
    "poison blade": Spell("poison blade", 12, "physical", 15, "a quick strike with a toxic edge.", "poison", 3),
    "shadow step": Spell("shadow step", 18, "physical", 25, "strikes suddenly from the shadows."),
    "throat slit": Spell("throat slit", 25, "physical", 30, "devastating attack.", "bleed", 3),
    "paralyzing dart": Spell("paralyzing dart", 15, "physical", 10, "ranged attack that stuns.", "stun", 2),

    # archer
    "piercing arrow": Spell("piercing arrow", 12, "physical", 18, "a high velocity arrow.", "bleed", 2),
    "volley": Spell("volley", 20, "physical", 25, "a rain of arrows."),
    "hunter mark": Spell("hunter mark", 15, "magic", 5, "exposes weak points.", "stun", 1),
    "venom arrow": Spell("venom arrow", 18, "physical", 15, "a toxic shot.", "poison", 3)
}

class_spell_pools = {
    "warrior": ["heavy strike", "shield bash", "rend", "warcry"],
    "mage": ["fireball", "ice shard", "lightning bolt", "venom blast"],
    "rogue": ["poison blade", "shadow step", "throat slit", "paralyzing dart"],
    "archer": ["piercing arrow", "volley", "hunter mark", "venom arrow"]
}