class Spell:
    def __init__(self, name, mana_cost, damage_type, base_power, description):
        self.name = name
        self.mana_cost = mana_cost
        self.damage_type = damage_type
        self.base_power = base_power
        self.description = description

    def cast(self, caster, target):
        # check if caster has enough mana
        if caster.current_mana < self.mana_cost:
            return False, "not enough mana!"
            
        # deduct mana cost
        caster.current_mana -= self.mana_cost
        
        # calculate damage based on spell type and caster stats
        if self.damage_type == "physical":
            # physical abilities scale with attack damage
            total_damage = self.base_power + caster.attack_damage
        elif self.damage_type == "magic":
            # magical abilities scale with magic damage
            total_damage = self.base_power + caster.magic_damage
        else:
            # fallback for true damage or utility spells
            total_damage = self.base_power
            
        # apply damage to target and calculate exact amount mitigated
        start_hp = target.current_health
        target.take_damage(total_damage, self.damage_type)
        actual_damage = start_hp - target.current_health
        
        return True, f"used {self.name}! dealt {actual_damage} damage."

# dictionary holding all available abilities in the game
spell_database = {
    # warrior abilities
    "heavy strike": Spell("heavy strike", 15, "physical", 20, "a powerful physical blow."),
    "shield bash": Spell("shield bash", 10, "physical", 10, "bashes the enemy with a shield."),
    
    # mage abilities
    "fireball": Spell("fireball", 20, "magic", 35, "hurls a blazing fireball."),
    "ice shard": Spell("ice shard", 15, "magic", 25, "shoots a piercing shard of ice."),
    
    # rogue abilities
    "poison blade": Spell("poison blade", 12, "physical", 15, "a quick strike with a toxic edge."),
    "shadow step": Spell("shadow step", 18, "physical", 25, "strikes suddenly from the shadows.")
}