from items.equipment import Item, Consumable, Equipment

class Inventory:
    def __init__(self):
        # storage array for unequipped items
        self.bag = []
        
        # dictionary holding currently equipped gear
        self.equipped = {
            "weapon": None,
            "armor": None,
            "ring": None,
            "necklace": None
        }

    def add_item(self, item):
        # place an item into the bag
        self.bag.append(item)

    def equip(self, equipment, player):
        # validate the item can be equipped
        if equipment not in self.bag or equipment.item_type != "equipment":
            return False
            
        # unequip currently slotted item first
        current_gear = self.equipped[equipment.slot]
        if current_gear:
            self.unequip(equipment.slot, player)
            
        # dynamically apply new stats to player using reflection
        for stat, value in equipment.stats.items():
            current_val = getattr(player, stat, 0)
            setattr(player, stat, current_val + value)
            
        # move item from bag to equipped slot
        self.equipped[equipment.slot] = equipment
        self.bag.remove(equipment)
        return True

    def unequip(self, slot, player):
        # find the item in the slot
        equipment = self.equipped[slot]
        if not equipment:
            return False
            
        # dynamically remove stats from player
        for stat, value in equipment.stats.items():
            current_val = getattr(player, stat, 0)
            setattr(player, stat, current_val - value)
            
        # move item from equipped slot back to bag
        self.bag.append(equipment)
        self.equipped[slot] = None
        return True

    def auto_equip(self, player):
        # loop through every available slot
        for slot in self.equipped.keys():
            best_item = None
            best_score = -1
            
            # evaluate currently equipped item if it exists
            if self.equipped[slot]:
                best_item = self.equipped[slot]
                best_score = self.calculate_item_score(best_item, player.player_class)
                
            # check bag for better items for this specific slot
            for item in self.bag:
                if item.item_type == "equipment" and item.slot == slot:
                    score = self.calculate_item_score(item, player.player_class)
                    if score > best_score:
                        best_score = score
                        best_item = item
                        
            # equip the best item found if it is not already equipped
            if best_item and best_item != self.equipped[slot]:
                self.equip(best_item, player)

    def calculate_item_score(self, item, player_class):
        score = 0
        # weight the stats differently depending on the chosen class
        for stat, value in item.stats.items():
            if player_class == "warrior":
                if stat == "attack_damage" or stat == "armor":
                    score += value * 2
                elif stat == "max_health":
                    score += value * 1
                else:
                    score += value * 0.5
                    
            elif player_class == "mage":
                if stat == "magic_damage" or stat == "max_mana":
                    score += value * 2
                else:
                    score += value * 0.5
                    
            elif player_class == "rogue":
                if stat == "attack_damage" or stat == "speed":
                    score += value * 2
                else:
                    score += value * 0.5
                    
        return score