import pickle
import shutil
import pygame
import time
from data import map
import threading
import os

class yaml:
    from yaml import safe_load as _load
    from yaml import dump as _save

    def save(data,path):
        with open(path,'w',encoding='UTF-8') as file:
            yaml._save(data, file, allow_unicode=True, sort_keys=False)
    def load(path):
        with open(path,'r',encoding='UTF-8') as file:
            return yaml._load(file)

def get_date():
    return time.strftime("%d-%m-%Y", time.localtime())

def get_time():
    return time.strftime("%H:%M:%S", time.localtime())

def get_date_and_time():
    return time.strftime("%d-%m-%Y %H:%M:%S",time.localtime()).split(' ')

log_levels = {
    0: 'INFO',
    1: 'WARN',
    2: 'CHAT'
}
def log(text, level=0):
    date, _time = get_date_and_time()
    print(f'{date} [{_time}] {log_levels[level]}: {text}')

class Mask:
    ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    RU = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    Ru = ru+RU
    en = 'abcdefghijklmnopqrstuvwxyz'
    EN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    En = en+EN
    n = '1234567890'
    s = R"_-=`'~!@#$%^&*()+№;%:?><{}[]|\/,."+'"'
    all = Ru+En+n+s

class Player:
    def __init__(self,world,name,password):
        self.dir = 'data/users/'

        mask = Mask.En+'_1234567890'
        for s in name:
            if not (s in mask): raise Exception('Имя содержит недопустимые символы')

        mask = Mask.en+Mask.n
        for s in password:
            if not (s in mask): raise Exception('Пароль содержит недопустимые символы')
        if(not os.path.exists(self.dir)):
            os.makedirs(self.dir)
        if f'{name}.yaml' in os.listdir(self.dir):
            self.data = yaml.load(f'{self.dir}{name}.yaml')
        else:
            self.data = {
                'password': password,
                'pos':world.start,
                'speed':[0,0]}
            yaml.save(self.data,f'data/users/{name}.yaml')
        if password != self.data['password']:
            raise Exception('Неверный пароль!')

        self.name = name
        self.password = password

        self.world = world
        self.pos = self.data['pos']
        self.speed = self.data['speed']
        self.collision = False

    @property
    def x(self):
        return self.pos[0]
    @x.setter
    def x(self,num):
        self.pos[0] = 0 if num < 0 else (784 if num > 784 else num)

    @property
    def y(self):
        return self.pos[1]
    @y.setter
    def y(self,num):
        self.pos[1] = 0 if num < 0 else (496 if num > 496 else num)

    @property
    def sx(self):
        return self.speed[0]
    @sx.setter
    def sx(self,num):
        self.speed[0] = num

    @property
    def sy(self):
        return self.speed[1]
    @sy.setter
    def sy(self,num):
        self.speed[1] = num

    def save(self):
        if not os.path.exists(self.dir):os.mkdir()
        yaml.save(self.data,f'{self.dir}/{self.name}.yaml')

class block:
    def __init__(self, pos, type):
        self.pos = pos
        self.type = type
    @property
    def x(self):
        return self.pos[0]
    @x.setter
    def x(self,num):
        self.pos[0] = num

    @property
    def y(self):
        return self.pos[1]
    @y.setter
    def y(self,num):
        self.pos[1] = num

    def __dict__(self):
        return {'pos':self.pos,'type':self.type}
    def __str__(self):
        return str({'pos':self.pos,'type':self.type})
    def __repr__(self):
        return str({'pos':self.pos,'type':self.type})

map.block = block

class World:
    def __init__(self,server,speed,gravity):
        self.server = server
        self.players = []
        self.blocks = map.map_load("data/map.cubit")
        self.speed = speed
        self.gravity = gravity
        self.start = [0,0]

        for b in self.blocks:
            if b.type == "start":
                self.start = b.pos
                break

        threading.Timer(30,self.saving_timer).start()
    def saving_timer(self):
        self.save_map()
        threading.Timer(30,self.saving_timer).start()
    def save_map(self):
        map.map_dump(self.blocks,"data/map.cubit")
    def get_blocks(self):
        return [i.__dict__()for i in self.blocks]
    def pop_block(self, block):
        if block.__dict__() in self.get_blocks():
            self.blocks.pop(self.get_blocks().index(block.__dict__()))
    def add_block(self, block):
        if block.__dict__() not in self.get_blocks():
            self.blocks.append(block)

    def add_player(self,player):
        self.players.append(player)

    def create_player(self,*a,**b):
        player = Player(self,*a,**b)
        self.players.append(player)
        return player

    def pop_player(self,player,save=True):
        if save: player.save()
        self.players.pop(self.players.index(player))

    def update(self):
        while True:
            for player in self.players:
                collision = False

                if player.y < 495:
                    player.sy += self.gravity

                for other in self.players+self.blocks:
                    is_block = type(other) == block
                    if not is_block or other.type not in ["start","fantom"]:
                        if player != other:
                            others_rect = pygame.Rect(other.x,other.y,16,16)

                            near = False

                            if player.sx != 0:
                                players_rect = pygame.Rect(player.x+player.sx,player.y,16,16)
                                if players_rect.colliderect(others_rect):
                                    if not is_block:
                                        other.sx += player.sx/2
                                    if player.x < other.x:
                                        player.sx = (other.x-16)-player.x
                                        near = True
                                    elif player.x > other.x:
                                        player.sx = player.x-(other.x+16)
                                        near = True

                            if player.sy != 0:
                                players_rect = pygame.Rect(player.x,player.y+player.sy,16,16)
                                if players_rect.colliderect(others_rect):
                                    if not is_block:
                                        other.sy += player.sy/2
                                    if player.sy > 0:
                                        player.sy = (other.y-16)-player.y
                                        near = True
                                        collision = True
                                    else:
                                        player.sy = player.y-(other.y+16)
                                        near = True

                            if near:
                                if is_block:
                                    if other.type == "finish":
                                        player.x,player.y = self.world.start
                                        player.sy,player.sx = 0,0
                                        player.collision = False
                                    elif other.type == "killer":
                                        player.x,player.y = self.world.start
                                        player.sy,player.sx = 0,0
                                        player.collision = False
                                    elif other.type == "speed":
                                        player.sx *= 2
                                    player.mega_jump = other.type == "jumper"

                player.collision = collision
                player.y += player.sy*(2 if player.mega_jump and player.sy < 0 else 1)
                player.x += player.sx
                player.sx = 0

            time.sleep(self.server.fps)

    def get_players(self):
        pos = {}
        for player in self.players:
            pos[player.name] = player.pos
        return pos
