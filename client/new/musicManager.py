import threading
import random
import pygwin
import data
import time
import os

class musicManager:
    def __init__(self,volume):
        self.path = None
        self.music = None
        self._volume = volume
        threading.Thread(target=self.start,daemon=1).start()
    def start(self):
        while True:
            if pygwin.mixer.music.pos == -0.001:
                path = self.get_random_song()
                if path == self.path:
                    continue
                pygwin.mixer.music.load(path)
                pygwin.mixer.music.volume = (self._volume-6)/94
                pygwin.mixer.music.play()
                time.sleep(pygwin.mixer.music.length)
                pygwin.mixer.music.stop()
                pygwin.mixer.music = None
                time.sleep(1)
            else:
                time.sleep(pygwin.mixer.music.length-pygwin.mixer.music.pos+1)
    def get_random_song(self):
        return data.join(data.path,"music/"+random.choice(
                os.listdir(data.join(data.path,"music"))))
    def volume():
        def fget(self):
            if self.music == None:
                return self._volume
            else:
                return self.music.volume
        def fset(self, v):
            if self.music == None:
                self._volume = v
            else:
                self.music.volume = (v-6)/94
        def fdel(self):
            pass
        return locals()
    volume = property(**volume())
