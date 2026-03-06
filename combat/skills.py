class PassiveSkill:
    def __init__(self, name, description, cost, effect_type, power):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_type = effect_type
        self.power = power
        self.unlocked = False

skill_tree_database = {
    "vampirism": PassiveSkill("vampirism", "heal 10% of physical damage dealt.", 1, "life_steal", 0.10),
    "midas touch": PassiveSkill("midas touch", "increase gold drops by 25%.", 1, "gold_boost", 0.25),
    "second wind": PassiveSkill("second wind", "15% chance to dodge fatal blows.", 1, "cheat_death", 0.15),
    "mana flow": PassiveSkill("mana flow", "restore 5 mp after every turn.", 1, "mana_regen", 5),
    "berserker": PassiveSkill("berserker", "+20% dmg when below 30% hp.", 1, "low_hp_buff", 0.20)
}