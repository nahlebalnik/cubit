import os
import sys
import json
import random
import pygwin

try:
    path = sys._MEIPASS
except:
    path = "data"

def join(a,b):
    return os.path.join(a,b)

class config:
    def __init__(self,filename,default={}):
        self.filename = filename
        if not os.path.exists(filename):
            self.set(default)
    def get(self):
        return json.load(open(self.filename,"r",encoding="utf8"))
    def set(self,data):
        json.dump(data,open(self.filename,"w",encoding="utf8"))

conf = config("config.json",{
    "volume": 100,
    "address": "",
    "nickname": f"Player{random.randint(0,999)}",
    "password": ""
})

class block:
    def __init__(self,pos,type):
        self.pos = pos
        self.type = type
    def x():
        def fget(self):
            return self.pos[0]
        def fset(self, v):
            self.pos[0] = v
        def fdel(self):
            pass
        return locals()
    x = property(**x())

    def y():
        def fget(self):
            return self.pos[1]
        def fset(self, v):
            self.pos[1] = v
        def fdel(self):
            pass
        return locals()
    y = property(**y())

    def __dict__(self):
        return {"pos":self.pos,"type":self.type}

font = pygwin.font.font(join(path,"font.ttf"))
