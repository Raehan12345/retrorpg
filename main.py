from engine.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()

#to package the game, run this command: pyinstaller --noconsole --onefile --add-data "C:\Users\raeha\OneDrive\Desktop\retro_rpg\assets:assets" main.py