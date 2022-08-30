import pygame
import threading

class gifDrawer:
    def __init__(self,surfaces,fps):
        self.fps = fps
        self.surfaces = surfaces
        self.index = 0
        self.clock = pygame.time.Clock()
        self.start()
    def tick(self):
        while self.run:
            self.clock.tick(self.fps)
            self.index += 1
            if self.index >= len(self.surfaces):
                self.index = 0
    def start(self):
        self.run = True
        threading.Thread(target=self.tick,daemon=1).start()
    def stop(self):
        self.run = False
    def get_surface(self):
        return self.surfaces[self.index]
