import pygwin
import data
import random
from gifDrawing import gifDrawer
import copy
import os
import threading
import json

def main():
    blue = {"bg":(35,35,180),
            "fg":(160,160,250),
            "afg":(35,35,180),
            "abg":(160,160,250),
            "borderColor":(20,20,70)}

    red = {"bg":(180,35,35),
           "fg":(250,160,160),
           "afg":(180,35,35),
           "abg":(250,160,160),
           "borderColor":(70,20,20)}

    green = {"bg":(35,180,35),
             "fg":(160,250,160),
             "afg":(35,180,35),
             "abg":(160,250,160),
             "borderColor":(20,70,20)}

    yellow = {"bg":(180,180,35),
             "fg":(250,250,160),
             "afg":(180,180,35),
             "abg":(250,250,160),
             "borderColor":(70,70,20)}

    def run_online():
        nonlocal ip,nickname,password
        import game
        game.Game(True,ip.text,
                  nickname.text,
                  password.text).start()
        raise SystemExit

    def run_offline():
        import game
        game.Game(False).start()
        raise SystemExit

    def run_editor():
        import editor
        editor.main()
        raise SystemExit

    win = pygwin.create('Cubit - Меню',(500,500))
    base = pygwin.ui.base(win)

    base.put(pygwin.ui.button("Офлайн",lambda:run_offline(),
              height=75,width=300,fontSize=35,font=data.font,**blue),(100,182),0)
    base.put(pygwin.ui.button("Онлайн",lambda:base.selectPage(2),
              height=75,width=300,fontSize=35,font=data.font,**green),(100,262),0)
    base.put(pygwin.ui.button("Редактор",lambda:run_editor(),
              height=75,width=300,fontSize=35,font=data.font,**yellow),(100,342),0)
    base.put(pygwin.ui.button("Настройки",lambda:base.selectPage(1),
              height=75,width=300,fontSize=35,font=data.font,**red),(100,422),0)

    base.put(pygwin.ui.button("<",lambda:base.selectPage(0),
          height=75,width=75,fontSize=35,font=data.font,**red),(20,182),2)

    ip = pygwin.ui.entry("Айпи",
        height=75,width=300,fontSize=35,font=data.font)
    ip.text = data.conf.get()["address"]
    base.put(ip,(100,182),2)

    nickname = pygwin.ui.entry("Никнейм",
       height=75,width=300,fontSize=35,font=data.font)
    nickname.text = data.conf.get()["nickname"]
    base.put(nickname,(100,262),2)

    password = pygwin.ui.entry("Пароль",
       height=75,width=250,fontSize=35,font=data.font)
    password.text = data.conf.get()["password"]
    base.put(password,(100,342),2)

    save_password = pygwin.ui.checkBox(width=55)
    base.put(save_password,(355,342),2)
    base.put(pygwin.ui.label("Сохранить",size=17,font=data.font),(355,400),2)

    base.put(pygwin.ui.button("Зайти",lambda:run_online(),
          height=75,width=300,fontSize=35,font=data.font,**green),(100,422),2)


    base.put(pygwin.ui.button("<",lambda:base.selectPage(0),
          height=75,width=75,fontSize=35,font=data.font,**red),(20,182),1)

    base.put(pygwin.ui.label("Громкость музыки",font=data.font),(130,275),1)

    music_volume = pygwin.ui.slider(200)
    music_volume.set(data.conf.get()["volume"])
    base.put(music_volume,(150,300),1)

    base.put(pygwin.ui.label("0",size=17,font=data.font),(157,345),1)
    base.put(pygwin.ui.label("100",size=17,font=data.font),(323,345),1)


    gif = gifDrawer([i.scale((100,100)) for i in pygwin.image.load(data.join(data.path,"cubit.gif"))],5)
    logo = pygwin.image.load(data.join(data.path,"logo.png")).scale((190,70))
    logo_a = 0
    logo_b = False

    music = pygwin.mixer.music(data.join(data.path,"music/"+\
    random.choice(os.listdir(data.join(data.path,"music")))))
    music.play()
    music.volume = (music_volume.get()-6)/94

    run = True
    while run:
        for event in pygwin.getEvents():
            if event.type == pygwin.QUIT:
                run = False
        base.draw()

        l = copy.copy(logo)
        win.blit(l,(155,30+round(logo_a)))

        if not logo_b:
            logo_a += 0.5
            if logo_a >= 25:
                logo_b = True
        else:
            logo_a -= 0.5
            if logo_a <= 0:
                logo_b = False

        win.blit(gif.get_surface(),(100,75))

        password.hide = password.text != ""

        music.volume = (music_volume.get()-6)/94

        c = data.conf.get()
        c["volume"] = music_volume.get()
        c["address"] = ip.text
        c["nickname"] = nickname.text
        if save_password.get():
            c["password"] = password.text
        data.conf.set(c)

        win.update(30)

main()
