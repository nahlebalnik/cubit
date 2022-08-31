from tkinter import messagebox
from tkinter import filedialog
from tkinter import Tk
import socket
import threading
import copy
import pickle
import pygwin
import data
import map
import time

map.block = data.block

class player:
    def __init__(self):
        self.pos = [0,0]
        self.speed = [0,0]
        self.collision = False
        self.mega_jump = False

    def x():
        def fget(self):
            return self.pos[0]
        def fset(self, v):
            self.pos[0] = 0 if v < 0 else (784 if v > 784 else v)
        def fdel(self):
            pass
        return locals()
    x = property(**x())

    def y():
        def fget(self):
            return self.pos[1]
        def fset(self, v):
            self.pos[1] = 0 if v < 0 else (496 if v > 496 else v)
        def fdel(self):
            pass
        return locals()
    y = property(**y())

    def sx():
        def fget(self):
            return self.speed[0]
        def fset(self, v):
            self.speed[0] = v
        def fdel(self):
            pass
        return locals()
    sx = property(**sx())

    def sy():
        def fget(self):
            return self.speed[1]
        def fset(self, v):
            self.speed[1] = v
        def fdel(self):
            pass
        return locals()
    sy = property(**sy())

class Game:
    def __init__(self,online,ip=None,nick=None,
                 pswd=None,preview=False,blocks=None):
        if online:
            self.win = pygwin.create('Cubit - Онлайн',(800,512))
            self.module = Online(self,ip,nick,pswd)
            self.blocks = []
        else:
            if preview:
                self.win = pygwin.create('Cubit - Предпросмотр',(800,512))
                self.blocks = blocks
                self.module = Preview(self)
            else:
                self.win = pygwin.create('Cubit - Офлайн',(800,512))
                self.module = Offline(self)
                self.blocks = []
        self.players = {}
        self.player = player()
        self.online = online
        self.speed = 3
        self.gravity = 0.8
        self.blocks_surface = pygwin.surface((800,512))
        self.inventory = {
            "normal":[(200,200,200),"Бетон"],
            "finish":[(250,200,100),"Финиш"],
            "killer":[(200,100,100),"Киллер"],
            "fantom":[(195,195,195),"Фантом"],
            "jumper":[(100,200,100),"Батут"],
            "speed":[(100,100,200),"Скорость"]
        }
        if not online and preview:
            self.update_blocks()

    def update_blocks(self):
        self.blocks_surface.fill((0,0,0,0))
        for b in self.blocks:
            self.blocks_surface.draw.rect(self.inventory[b["type"]][0],[*b["pos"],16,16])

    def create_block(self,pos,type):
        self.delete_block(pos)
        self.blocks.append({"pos":pos,"type":type})
        try:self.blocks_surface.draw.rect(self.inventory[type][0],[*pos,16,16])
        except:pass

    def delete_block(self,pos):
        for i in self.blocks:
            if i["pos"][0] == pos[0]:
                if i["pos"][1] == pos[1]:
                    self.blocks.remove(i)
                    self.blocks_surface.draw.rect((0,0,0,0),[*pos,16,16])
                    break

    def start(self):
        self.module.past_init()
        self.run = True
        while self.run:
            for event in pygwin.getEvents():
                if event.type == pygwin.QUIT:
                    self.run = False
                self.module.event_handle(event)

            self.win.fill((25,25,25))

            if pygwin.keyboard.isprs("d"):
                self.player.sx = self.speed
            elif pygwin.keyboard.isprs("a"):
                self.player.sx = -self.speed
            if pygwin.keyboard.isprs("space"):
                if self.player.collision or self.player.y == 496:
                    self.player.sy = -8

            self.module.update()

            for p in self.players.items():
                t = data.font.render(p[0],20,(120,120,120))
                self.win.blit(t,(p[1][0]+8-t.size[0]/2,
                            p[1][1]-5-t.size[1]))
                self.win.draw.rect((50,50,50),[*p[1],16,16])
            self.win.blit(self.blocks_surface,(0,0))
            self.win.draw.rect((150,150,150),[*self.player.pos,16,16])

            self.module.post_update()
            self.win.blit(self.win.fps,(0,0))
            self.win.update(60)

class Online:
    def __init__(self,game,host,nick,pswd):
        self.game = game
        self.nick = nick
        self.editable = False

        self.isEscape = False
        self.escape_a = 1000

        self.escape_text = data.font.render("Выйти",50,(200,200,200))
        self.reload_text = data.font.render("Заново",50,(200,200,200))

        self.escape_text_active = data.font.render("Выйти",50,(150,150,150))
        self.reload_text_active = data.font.render("Заново",50,(150,150,150))

        self.escape_bg = pygwin.surface((800,512))
        self.escape_bg.fill((0,0,0,50))
        self.escape_rect = pygwin.rect(250,156,300,200)
        self.escape_rect_1 = pygwin.rect(250,156,300,100)
        self.escape_rect_2 = pygwin.rect(250,256,300,100)
        self.escape_bg.draw.rect((0,0,0,100),self.escape_rect,0,10)
        self.escape_bg.draw.rect((0,0,0,200),self.escape_rect,5,10)

        self.tab_text = data.font.render("Инвентарь",50,(200,200,200))
        self.tab_bg = pygwin.surface((700,412))
        self.tab_bg.draw.rect((0,0,0,100),[0,0,700,410],0,10)
        self.tab_bg.draw.rect((0,0,0,200),[0,0,700,410],5,10)
        self.tab_bg.draw.rect((0,0,0,200),[0,60,700,350],5,10)
        self.tab_bg.blit(self.tab_text,(400-(self.tab_text.size[0]/2)-50,10))
        self.tab_a = -1000
        self.isTab = False
        self.localBlockType = "normal"

        protocol = "2.2"

        try:
            if ":" in host:
                splitted = host.split(":")

                ip = splitted[0]
                port = int(splitted[1])
            else:
                ip = host
                port = 12000

            self.socket = socket.socket()
            self.socket.connect((ip,port))
            self.socket.setblocking(False)
            self.socket.settimeout(5)
            self.send({'name':nick,
                       'password':pswd,
                       'version':protocol})
        except Exception as e:
            self.showError(e)

        threading.Thread(target=self.recv,daemon=1).start()
    def past_init(self):
        pass
    def showError(self,error):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Ошибка.", str(error))
        root.destroy()
    def recv(self):
        while True:
            try:
                data = self.socket.recv(1024*40)
                data = pickle.loads(data)
            except ConnectionAbortedError:
                break
            except ConnectionResetError:
                break
            except socket.timeout:
                break
            except Exception as e:
                self.showError(e)
            else:
                if 'players' in data:
                    self.game.players = data['players']
                    self.game.player.pos = self.game.players.pop(self.nick)
                if 'blocks' in data:
                    old = copy.copy(self.game.blocks)
                    new = [i.__dict__() for i in map.map_loads(data['blocks'])]
                    for i,o in enumerate(new):
                        if o not in old:
                            self.game.create_block(o['pos'],o['type'])
                    for i,n in enumerate(old):
                        if n not in new:
                            self.game.delete_block(n['pos'])
                if 'editable' in data:
                    self.editable = data['editable']
                if 'error' in data:
                    self.showError(data['error'])
        self.close()
        print("server closed")
    def update(self):
        if not self.isEscape:
            data = {'move': {'x':None,'y':None},'block':{}}

            keys = pygwin.keyboard.gprs()

            if keys["a"]:
                data['move']['x'] = 'left'
            if keys["d"]:
                data['move']['x'] = 'right'
            if keys["space"]:
                data['move']['y'] = 'jump'

            if self.editable:
                button = pygwin.mouse.get_pressed()
                if button[0] or button[2]:
                    mouseX, mouseY = pygwin.mouse.get_pos()
                    pos = (mouseX//16*16, mouseY//16*16)
                if button[2] and (not button[0]):
                    data['block'].update({'create':{
                        'pos':pos,'type':self.localBlockType}})
                if button[0] and (not button[2]):
                    data['block'].update({'delete':{
                        'pos':pos,'type':self.localBlockType}})
            self.send(data)
    def post_update(self):
        if self.isEscape:
            if self.escape_a > 0:
                self.escape_a -= self.escape_a/10
                self.draw_escape()
            if self.tab_a > -1000:
                self.tab_a -= (1000+self.tab_a)/10
                self.draw_tab()
        elif self.isTab:
            if self.tab_a < 0:
                self.tab_a += self.tab_a*-1/10
                self.draw_tab()
            if self.escape_a < 1000:
                self.escape_a += (1000-self.escape_a)/10
                self.draw_escape()
        else:
            if self.tab_a > -1000:
                self.tab_a -= (1000+self.tab_a)/10
                self.draw_tab()
            if self.escape_a < 1000:
                self.escape_a += (1000-self.escape_a)/10
                self.draw_escape()
    def event_handle(self,event):
        if event.type == pygwin.KEYUP:
            if event.key == pygwin.K_TAB:
                if self.editable:
                    self.isTab = self.isTab != 1
                    if self.isTab: self.isEscape = False
            if event.key == pygwin.K_ESCAPE:
                if self.isTab:
                    self.isTab = False
                else:
                    self.isEscape = self.isEscape != 1
    def draw_tab(self):
        self.game.win.blit(self.tab_bg,(50+self.tab_a,50))
        p = pygwin.mouse.gpos()
        inv = list(self.game.inventory.items())
        i = 0
        for y in range(5):
            for x in range(10):
                r = pygwin.rect(50+x*70+self.tab_a,110+y*70,70,70)
                if r.contains(*p):
                    self.game.win.draw.rect((100,100,100,128),r,0,10)
                    if pygwin.mouse.isPressed("left"):
                        self.localBlockType = inv[i][0]
                if self.localBlockType == inv[i][0]:
                    self.game.win.draw.rect(inv[i][1][0],
                      [r.x+10,r.y+10,50,50])
                else:
                    self.game.win.draw.rect(inv[i][1][0],
                      [r.x+20,r.y+20,30,30])
                i += 1
                if i >= len(inv): break
            if i >= len(inv): break
        i = 0
        for y in range(5):
            for x in range(10):
                r = pygwin.rect(50+x*70+self.tab_a,110+y*70,70,70)
                if r.contains(*p):
                    t = data.font.render(inv[i][1][1],20,(200,200,200))
                    tr = t.rect(p[0],p[1])
                    self.game.win.draw.rect((50,50,50),[tr.x,tr.y-30,tr.w+10,tr.h+10])
                    self.game.win.draw.rect((20,20,20),[tr.x,tr.y-30,tr.w+10,tr.h+10],2)
                    self.game.win.blit(t,(p[0]+5,p[1]-25))
                i += 1
                if i >= len(inv): break
            if i >= len(inv): break
    def draw_escape(self):
        self.game.win.blit(self.escape_bg,(self.escape_a,0))

        pos = pygwin.mouse.gpos()

        reload_text_center = (self.escape_a+self.escape_rect_1.x+self.escape_rect_1.w/2-self.reload_text.size[0]/2,
                            self.escape_rect_1.y+self.escape_rect_1.h/2-self.reload_text.size[1]/2)
        if self.escape_rect_1.contains(*pos):
            self.game.win.blit(self.reload_text_active,reload_text_center)
            if pygwin.mouse.isPressed("left"):
                self.send({"respawn":None})
        else:
            self.game.win.blit(self.reload_text,reload_text_center)

        escape_text_center = (self.escape_a+self.escape_rect_2.x+self.escape_rect_2.w/2-self.escape_text.size[0]/2,
                              self.escape_rect_2.y+self.escape_rect_2.h/2-self.escape_text.size[1]/2)
        if self.escape_rect_2.contains(*pos):
            self.game.win.blit(self.escape_text_active,escape_text_center)
            if pygwin.mouse.isPressed("left"):
                import main
                main.main()
                raise SystemExit
        else:
            self.game.win.blit(self.escape_text,escape_text_center)

        if not self.escape_rect.contains(*pos):
            if pygwin.mouse.isPressed("left"):
                self.isEscape = False
    def close(self):
        try: self.socket.close()
        except: pass
        import main
        main.main()
        raise SystemExit
    def send(self,data):
        try: self.socket.send(pickle.dumps(data))
        except: pass

class Offline:
    def __init__(self,game):
        self.game = game

        self.start = [0,0]

        self.isEscape = False
        self.escape_a = 1000

        self.escape_text = data.font.render("Выйти",50,(200,200,200))
        self.load_text = data.font.render("Загрузить",50,(200,200,200))
        self.reload_text = data.font.render("Заново",50,(200,200,200))

        self.escape_text_active = data.font.render("Выйти",50,(150,150,150))
        self.load_text_active = data.font.render("Загрузить",50,(150,150,150))
        self.reload_text_active = data.font.render("Заново",50,(150,150,150))

        self.escape_bg = pygwin.surface((800,512))
        self.escape_bg.fill((0,0,0,50))
        self.escape_rect = pygwin.rect(250,156,300,200)
        self.escape_rect_1 = pygwin.rect(250,156,300,66)
        self.escape_rect_2 = pygwin.rect(250,222,300,66)
        self.escape_rect_3 = pygwin.rect(250,288,300,66)
        self.escape_bg.draw.rect((0,0,0,100),self.escape_rect,0,10)
        self.escape_bg.draw.rect((0,0,0,200),self.escape_rect,5,10)
    def past_init(self):
        pass
    def update(self):
        if not self.isEscape:
            collision = False

            if self.game.player.y < 495:
                self.game.player.sy += self.game.gravity

            for other in self.game.blocks:
                others_rect = pygwin.rect(other["pos"][0],other["pos"][1],16,16)

                near = False

                if self.game.player.sx != 0:
                    players_rect = pygwin.rect(self.game.player.x+self.game.player.sx,
                                               self.game.player.y,16,16)
                    if players_rect.collide(others_rect):
                        if self.game.player.x < other["pos"][0]:
                            self.game.player.sx = (other["pos"][0]-16)-self.game.player.x
                            near = True
                        elif self.game.player.x > other["pos"][0]:
                            self.game.player.sx = self.game.player.x-(other["pos"][0]+16)
                            near = True

                if self.game.player.sy != 0:
                    players_rect = pygwin.rect(self.game.player.x,self.game.player.y+self.game.player.sy,16,16)
                    if players_rect.collide(others_rect):
                        if self.game.player.sy > 0:
                            self.game.player.sy = (other["pos"][1]-16)-self.game.player.y
                            near = True
                            collision = True
                        else:
                            self.game.player.sy = self.game.player.y-(other["pos"][1]+16)
                            near = True

                if near:
                    if other["type"] == "finish":
                        self.game.player.x,self.game.player.y = self.start
                        self.game.player.sy,self.game.player.sx = 0,0
                        self.game.player.collision = False
                    elif other["type"] == "killer":
                        self.game.player.x,self.game.player.y = self.start
                        self.game.player.sy,self.game.player.sx = 0,0
                        self.game.player.collision = False
                    elif other["type"] == "speed":
                        self.game.player.sx *= 2
                    self.game.player.mega_jump = other["type"] == "jumper"

            self.game.player.collision = collision

            self.game.player.y += self.game.player.sy * (2 if self.game.player.mega_jump and self.game.player.sy < 0 else 1)
            self.game.player.x += self.game.player.sx
            self.game.player.sx = 0
    def post_update(self):
        if self.isEscape:
            if self.escape_a > 0:
                self.escape_a -= self.escape_a/10
                self.draw_escape()
        else:
            if self.escape_a < 1000:
                self.escape_a += (1000-self.escape_a)/10
                self.draw_escape()
    def event_handle(self,event):
        if event.type == pygwin.KEYUP:
            if event.key == pygwin.K_ESCAPE:
                self.isEscape = self.isEscape != 1
    def draw_escape(self):
        self.game.win.blit(self.escape_bg,(self.escape_a,0))

        pos = pygwin.mouse.gpos()

        load_text_center = (self.escape_a+self.escape_rect_1.x+self.escape_rect_1.w/2-self.load_text.size[0]/2,
                            self.escape_rect_1.y+self.escape_rect_1.h/2-self.load_text.size[1]/2)
        if self.escape_rect_1.contains(*pos):
            self.game.win.blit(self.load_text_active,load_text_center)
            if pygwin.mouse.isPressed("left"):
                tk = Tk()
                tk.withdraw()
                f = filedialog.askopenfilename(title="Загрузить карту",
                           filetypes=(("Cubit файлы","*.cubit"),("All files","*.*")),defaultextension=".cubit")
                if f != None and f != "":
                    l = map.map_load(f)
                    self.game.blocks = [{"pos":i.pos,"type":i.type} for i in l]
                tk.destroy()
                found = False
                for b in copy.copy(self.game.blocks):
                    if b["type"] == "start":
                        if not found:
                            self.start = b["pos"]
                            found = True
                        self.game.blocks.remove(b)
                self.game.player.pos = copy.copy(self.start)
                self.game.player.speed = [0,0]
                self.game.player.collision = False
                self.game.update_blocks()
        else:
            self.game.win.blit(self.load_text,load_text_center)


        reload_text_center = (self.escape_a+self.escape_rect_2.x+self.escape_rect_2.w/2-self.reload_text.size[0]/2,
                            self.escape_rect_2.y+self.escape_rect_2.h/2-self.reload_text.size[1]/2)
        if self.escape_rect_2.contains(*pos):
            self.game.win.blit(self.reload_text_active,reload_text_center)
            if pygwin.mouse.isPressed("left"):
                self.game.player.pos = copy.copy(self.start)
                self.game.player.speed = [0,0]
                self.game.player.collision = False
        else:
            self.game.win.blit(self.reload_text,reload_text_center)

        escape_text_center = (self.escape_a+self.escape_rect_3.x+self.escape_rect_3.w/2-self.escape_text.size[0]/2,
                              self.escape_rect_3.y+self.escape_rect_3.h/2-self.escape_text.size[1]/2)
        if self.escape_rect_3.contains(*pos):
            self.game.win.blit(self.escape_text_active,escape_text_center)
            if pygwin.mouse.isPressed("left"):
                import main
                main.main()
                raise SystemExit
        else:
            self.game.win.blit(self.escape_text,escape_text_center)

        if not self.escape_rect.contains(*pos):
            if pygwin.mouse.isPressed("left"):
                self.isEscape = False

class Preview:
    def __init__(self,game):
        self.game = game
        self.start = [0,0]
        for b in copy.copy(self.game.blocks):
            if b["type"] == "start":
                self.start = b["pos"]
                self.game.blocks.remove(b)
                break
    def past_init(self):
        self.game.player.pos = copy.copy(self.start)
        self.game.player.speed = [0,0]
        self.game.player.collision = False
    def update(self):
        collision = False

        if self.game.player.y < 495:
            self.game.player.sy += self.game.gravity

        for other in self.game.blocks:
            if other["type"] not in ["start","fantom"]:
                others_rect = pygwin.rect(other["pos"][0],other["pos"][1],16,16)

                near = False

                if self.game.player.sx != 0:
                    players_rect = pygwin.rect(self.game.player.x+self.game.player.sx,
                                               self.game.player.y,16,16)
                    if players_rect.collide(others_rect):
                        if self.game.player.x < other["pos"][0]:
                            self.game.player.sx = (other["pos"][0]-16)-self.game.player.x
                            near = True
                        elif self.game.player.x > other["pos"][0]:
                            self.game.player.sx = self.game.player.x-(other["pos"][0]+16)
                            near = True

                if self.game.player.sy != 0:
                    players_rect = pygwin.rect(self.game.player.x,self.game.player.y+self.game.player.sy,16,16)
                    if players_rect.collide(others_rect):
                        if self.game.player.sy > 0:
                            self.game.player.sy = (other["pos"][1]-16)-self.game.player.y
                            near = True
                            collision = True
                        else:
                            self.game.player.sy = self.game.player.y-(other["pos"][1]+16)
                            near = True

                if near:
                    if other["type"] == "finish":
                        self.game.player.x,self.game.player.y = self.start
                        self.game.player.sy,self.game.player.sx = 0,0
                        self.game.player.collision = False
                    elif other["type"] == "killer":
                        self.game.player.x,self.game.player.y = self.start
                        self.game.player.sy,self.game.player.sx = 0,0
                        self.game.player.collision = False
                    elif other["type"] == "speed":
                        self.game.player.sx *= 2
                    self.game.player.mega_jump = other["type"] == "jumper"

        self.game.player.collision = collision

        self.game.player.y += self.game.player.sy * (2 if self.game.player.mega_jump and self.game.player.sy < 0 else 1)
        self.game.player.x += self.game.player.sx
        self.game.player.sx = 0
    def event_handle(self,event):
        if event.type == pygwin.KEYUP:
            if event.key == pygwin.K_ESCAPE:
                import editor
                editor.main(self.game.blocks+[{"pos":self.start,"type":"start"}])
                raise SystemExit
    def post_update(self):
        pass

if __name__ == '__main__':
    Game(False).start()
