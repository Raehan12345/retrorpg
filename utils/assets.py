import pygame
import os
import sys

class AssetManager:
    _cache = {}

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_sprite_sheet(folder, filename, frame_width=128, frame_height=128, is_layer=False):
        key = f"{folder}/{filename}"
        if key in AssetManager._cache:
            return AssetManager._cache[key]
            
        # FIX: Use resource_path to find assets inside the EXE internal memory
        path = AssetManager.resource_path(os.path.join("assets", "sprites", folder, filename))
        
        frames = []
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
            cols = sheet.get_width() // frame_width
            
            for x in range(cols):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x * frame_width, 0, frame_width, frame_height))
                # Admurin assets are 128x128; we scale to 96x96 for world visibility
                frame = pygame.transform.scale(frame, (96, 96))
                frames.append(frame)
        else:
            # Fallback to green square if the file is truly missing
            dummy = pygame.Surface((96, 96), pygame.SRCALPHA)
            if not is_layer:
                dummy.fill((50, 200, 50)) 
            frames.append(dummy)
            
        AssetManager._cache[key] = frames
        return frames