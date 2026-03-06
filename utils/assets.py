import pygame
import os

class AssetManager:
    _cache = {}

    @staticmethod
    def load_sprite_sheet(folder, filename, frame_width=128, frame_height=128, is_layer=False):
        key = f"{folder}/{filename}"
        if key in AssetManager._cache:
            return AssetManager._cache[key]
            
        base_dir = os.path.abspath(os.getcwd())
        path = os.path.join(base_dir, "assets", "sprites", folder, filename)
        
        frames = []
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
            cols = sheet.get_width() // frame_width
            
            for x in range(cols):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x * frame_width, 0, frame_width, frame_height))
                # ENLARGED SCALING: Changed from 64x64 to 96x96 for better visibility
                frame = pygame.transform.scale(frame, (96, 96))
                frames.append(frame)
        else:
            dummy = pygame.Surface((96, 96), pygame.SRCALPHA)
            if not is_layer:
                dummy.fill((50, 200, 50)) 
            frames.append(dummy)
            
        AssetManager._cache[key] = frames
        return frames