# Retro RPG: Python Edition

A modular, 2D top-down RPG built with **Pygame-CE**. This project features a dynamic layered equipment system, procedural dungeon generation with connectivity validation, and a classic turn-based combat engine.

---

## 🚀 Features

### 🎨 Dynamic Visuals
* **Layered Sprite System:** Leverages the *Monster Pack Character 2* by Admurin, allowing weapons (Swords, Bows, Staffs) to be rendered dynamically over the base character sprite in real-time.
* **Pixel-Perfect Animations:** Supports 4-frame idle loops and is structured to expand into 6-frame attack and movement sequences.
* **Equipment Preview:** Features a compact 120x120 character preview in the inventory menu that updates instantly as gear is changed.

### 🗺️ World & Exploration
* **Procedural Dungeons:** Randomly generated maps utilizing a **Flood-Fill Algorithm** to ensure 100% path connectivity between the player spawn and the portal.
* **Clamped Camera System:** A "follow-cam" that keeps the player centered while strictly preventing the viewport from showing the black void outside map boundaries.
* **Interactive Entities:** Features Chests for loot, Forges for item upgrading, and Enemy encounters.

### ⚔️ Combat & Systems
* **Turn-Based Battle Engine:** Classic RPG combat including physical attacks, magic spells, and passive skill checks (e.g., Berserk/Low-HP buffs).
* **Inventory Management:** Integrated system for equipping, using consumables, and dismantling gear for crafting materials (Shards).
* **The Forge:** A risk-reward upgrade system where items can be leveled up using collected Shards.

---

## ⌨️ Controls

| Key | Action |
| :--- | :--- |
| **W / A / S / D** | Move Character / Navigate Menus |
| **I** | Open or Close Inventory |
| **C** | Open Character Status Info |
| **L** | Open Level Up / Stats Menu |
| **ENTER** | Interact with World / Select Menu Option |
| **SPACE** | Auto-Equip Best Gear (while in Inventory) |
| **X** | Dismantle Item for Shards (while in Inventory) |
| **F5** | Quick Save Game |
| **ESC** | Close Current Menu / Exit Forge / Return to Explorer |

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.10+
* Pygame-CE

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/retro-rpg-python.git](https://github.com/yourusername/retro-rpg-python.git)
   cd retro-rpg-python
2. Install Dependencies
    run: pip install pygame-ce 

# Running the game
To Start the Adventure, run:
python main.py