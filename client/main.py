from threading import Thread
from socket import socket as Socket
import time, pickle
import Yaml, Mask
from UI import *

class Player:
    def __init__(self):
        self.pos = (0,0)
        self.image = pygame.Surface((16,16))
        self.image.fill([150,150,150])
        pygame.draw.rect(self.image,(200,0,0),(0,0,16,16),1)

    def draw(self):
        screen.blit(self.image,self.pos)

class Online:
    def __init__(self,app,host,name,password):
        self.app = app
        self.socket = Socket()
        try:
            try:
                self.socket.connect((host.split(":")[0],int(host.split(":")[1])))
            except:
                self.socket.connect((host,12000))
            self.send({'name':name,'password':password,'version':self.app.version})
        except Exception as error:
            self.set_label(str(error))
        else:
            self.name = name
            self.password = password
            Thread(target=self.recv,daemon=True).start()

        self.info = True
        self.player = Player()

        self.image = pygame.Surface((16,16))
        self.image.fill([148,59,196])
        self.localBLockType = 'pisun'
        self.players = []
        self.blocks = []

    def set_label(self,text):
        if text == None:
            self.app.objects[0].labels[0][0].text = ''
            self.app.objects[0].labels[0][1].text = ''
        elif len(text) > 70:
            self.app.objects[0].labels[0][0].text = text[:70]
            self.app.objects[0].labels[0][1].text = text[70:]
        else:
            self.app.objects[0].labels[0][0].text = text

    def close(self):
        try: self.socket.close()
        except: pass

    def recv(self):
        while True:
            try:
                data = self.socket.recv(1024)
                data = pickle.loads(data)
            except ConnectionAbortedError:
                break
            except ConnectionResetError:
                break
            except Exception as error:
                self.set_label(str(error))
            else:
                if 'players' in data:
                    self.players = data['players']
                    self.player.pos = self.players.pop(self.name)
                if 'blocks' in data:
                    self.blocks = data['blocks']
                if 'error' in data:
                    self.set_label(str(data['error']))
        self.close()
        self.app.pop(self)

    def send(self,data):
        try: self.socket.send(pickle.dumps(data))
        except: pass

    def event(self,events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    self.app.pop(self)
                    self.set_label(None)
                elif event.key == pygame.K_F3:
                    self.info = not self.info

    def update(self):
        keys = pygame.key.get_pressed()

        data = {'move': {'x':None,'y':None},'block':{}}

        if keys[pygame.K_a]:
            data['move']['x'] = 'left'
        if keys[pygame.K_d]:
            data['move']['x'] = 'right'
        if keys[pygame.K_SPACE]:
            data['move']['y'] = 'jump'

        button = pygame.mouse.get_pressed()
        if button[0] or button[2]:
            mouseX, mouseY = pygame.mouse.get_pos()
            pos = (mouseX//16*16, mouseY//16*16)
        if button[2] and (not button[0]):
            data['block'].update({'create':{
            'pos':pos,'type':self.localBLockType}})
        if button[0] and (not button[2]):
            data['block'].update({'delete':{
            'pos':pos,'type':self.localBLockType}})
        self.send(data)

    def draw(self):
        self.player.draw()
        for name in self.players:
            screen.blit(self.image,self.players[name])

            image = font(16).render(name,True,[200,0,0])
            rect = image.get_rect(centerx=self.players[name][0]+8,bottom=self.players[name][1])
            screen.blit(image,rect)
        for b in self.blocks:
            image = pygame.Surface((16,16))
            if b["type"] == "normal":
                image.fill([255,255,255])
            else:
                pygame.draw.rect(image,(255,0,255),[0,0,8,8])
                pygame.draw.rect(image,(0,0,0),[8,0,8,8])
                pygame.draw.rect(image,(0,0,0),[0,8,8,8])
                pygame.draw.rect(image,(255,0,255),[8,8,8,8])
            screen.blit(image,b["pos"])
        if self.info:
            screen.blit(font(16).render(self.app.get_fps_string(),1,[200,0,0]),[5,4])


class App:
    def __init__(self):
        self.objects = []

        self.u_clock = pygame.time.Clock()
        self.d_clock = pygame.time.Clock()
        self.fps = 60
        self.background = [30,30,30]
        self.run = True
        self.version = '2.1'

    def add(self,object):
        self.objects.append(object)

    def pop(self,object):
        if object in self.objects:
            self.objects.pop(self.objects.index(object))

    def get_fps_string(self):
        return f'{int(self.d_clock.get_fps())}/{int(self.u_clock.get_fps())}'

    def update(self):
        QUIT = pygame.event.Event(pygame.QUIT)
        Thread(target=self.draw,daemon=True).start()

        while self.run:
            self.events = pygame.event.get()
            if QUIT in self.events:
                self.run = False

            if len(self.objects) > 0:
                object = self.objects[-1]
                object.event(self.events)
                object.update()
            self.u_clock.tick(self.fps)

    def draw(self):
        time.sleep(0.5)
        while self.run:
            screen.fill(self.background)

            if len(self.objects) > 0:
                object = self.objects[-1]
                object.draw()
            pygame.display.update()
            self.d_clock.tick(self.fps)

if __name__ == '__main__':
    app = App()

    menu = Menu(app)
    app.add(menu)

    def nun():
        host = menu.inputs[0][0].text
        name = menu.inputs[0][1].text
        password = menu.inputs[0][2].text
        try: Yaml.save({'host':host,'name':name,'password':password},'config.yaml')
        except: pass
        if host and name and password:
            app.add(Online(app,host,name,password))
            # app.player.connect(host,name,password)

    # button = pos,size,name,func=None,*args
    menu.add(0,(300,311),(200,40),'Начать',nun)

    # input = pos,size,hide,max,mask
    menu.add(1,(300,161),(200,40),'Айпи',99,Mask.En+'.1234567890:')
    menu.add(1,(300,211),(200,40),'Имя',12,Mask.En+'_1234567890')
    menu.add(1,(300,261),(200,40),'Пароль',16,Mask.en+Mask.n)
    # label = center,text max 70
    menu.add(2,(400,371),'')
    menu.add(2,(400,401),'')

    try:
        data = Yaml.load('config.yaml')
        for index,name in enumerate(['host','name','password']):
            text = str(data[name])
            if len(text) > menu.inputs[0][index].max:
                raise Exception
            for s in text:
                if not (s in menu.inputs[0][index].mask):
                    raise Exception
        menu.inputs[0][0].text = data['host']
        menu.inputs[0][1].text = data['name']
        menu.inputs[0][2].text = data['password']
    except: pass
    app.update()
