import copy

class Inventory:
    def __init__(self):
        self.equipped = {"weapon": None, "armor": None, "ring": None, "necklace": None}
        self.bag = []

    def add_item(self, item):
        if item.item_type == "consumable":
            for b_item in self.bag:
                if b_item.name == item.name:
                    b_item.quantity += getattr(item, 'quantity', 1)
                    return
        
        new_item = copy.deepcopy(item)
        if not hasattr(new_item, 'quantity'): new_item.quantity = 1
        self.bag.append(new_item)

    def remove_item(self, item):
        if hasattr(item, 'quantity') and item.quantity > 1:
            item.quantity -= 1
        else:
            if item in self.bag: self.bag.remove(item)

    def equip(self, item, player):
        if item.item_type == "equipment":
            slot = item.slot
            if self.equipped[slot]: self.unequip(slot, player)
            self.equipped[slot] = item
            self.remove_item(item)
            self.apply_stats(item, player, 1)

    def unequip(self, slot, player):
        item = self.equipped[slot]
        if item:
            self.add_item(item)
            self.equipped[slot] = None
            self.apply_stats(item, player, -1)

    def apply_stats(self, item, player, multiplier):
        for stat, value in item.stats.items():
            current = getattr(player, stat, 0)
            setattr(player, stat, current + (value * multiplier))

    def auto_equip(self, player):
        best_items = {}
        for item in self.bag:
            if item.item_type == "equipment":
                slot = item.slot
                score = sum(item.stats.values())
                if slot not in best_items or score > best_items[slot][1]:
                    best_items[slot] = (item, score)
        
        for slot, (item, score) in best_items.items():
            curr_equipped = self.equipped[slot]
            if not curr_equipped or score > sum(curr_equipped.stats.values()):
                self.equip(item, player)