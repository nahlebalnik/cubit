import threading
from tkinter import filedialog
from tkinter import Tk
import pygwin
import copy
import data
import map
import game

map.block = data.block

def main(b=None):
    win = pygwin.create('Cubit - Редактор',(800,512))

    if b == None:
        blocks = [data.block([0,0],"start"),
                  data.block([784,496],"finish")]
    else:
        blocks = [data.block(i["pos"],i["type"]) for i in b]

    blocks_surface = pygwin.surface((800,512))
    localBlockType = "normal"

    inventory = {
        "normal":[(200,200,200),"Бетон"],
        "start":[(150,250,100),"Старт"],
        "finish":[(250,200,100),"Финиш"],
        "killer":[(200,100,100),"Киллер"],
        "fantom":[(195,195,195),"Фантом"],
        "jumper":[(100,200,100),"Батут"],
        "speed":[(100,100,200),"Скорость"]
    }

    def update_blocks():
        nonlocal blocks_surface,blocks
        blocks_surface.fill((0,0,0,0))
        for b in blocks:
            blocks_surface.draw.rect(inventory[b.type][0],[*b.pos,16,16])

    def create_block(pos,type):
        delete_block(pos)
        if type in ["start","finish"]:
            for i in copy.copy(blocks):
                if i.type == type:
                    blocks.remove(i)
                    blocks_surface.draw.rect((0,0,0,0),[*i.pos,16,16])
        blocks.append(data.block(pos,type))
        blocks_surface.draw.rect(inventory[type][0],[*pos,16,16])

    def delete_block(pos):
        for i in blocks:
            if i.pos[0] == pos[0]:
                if i.pos[1] == pos[1]:
                    blocks.remove(i)
                    blocks_surface.draw.rect((0,0,0,0),[*pos,16,16])
                    if i.type == "start":
                        create_block((0,0),"start")
                    elif i.type == "finish":
                        create_block((784,496),"finish")
                    break

    update_blocks()

    escape_text = data.font.render("Выйти",50,(200,200,200))
    load_text = data.font.render("Загрузить",50,(200,200,200))
    save_text = data.font.render("Сохранить",50,(200,200,200))

    escape_text_active = data.font.render("Выйти",50,(150,150,150))
    load_text_active = data.font.render("Загрузить",50,(150,150,150))
    save_text_active = data.font.render("Сохранить",50,(150,150,150))

    escape_bg = pygwin.surface((800,512))
    escape_bg.fill((0,0,0,50))
    escape_rect = pygwin.rect(250,156,300,200)
    escape_rect_1 = pygwin.rect(250,156,300,66)
    escape_rect_2 = pygwin.rect(250,222,300,66)
    escape_rect_3 = pygwin.rect(250,288,300,66)
    escape_bg.draw.rect((0,0,0,100),escape_rect,0,10)
    escape_bg.draw.rect((0,0,0,200),escape_rect,5,10)

    escape_a = 1000

    tab_text = data.font.render("Инвентарь",50,(200,200,200))
    tab_bg = pygwin.surface((700,412))
    tab_bg.draw.rect((0,0,0,100),[0,0,700,410],0,10)
    tab_bg.draw.rect((0,0,0,200),[0,0,700,410],5,10)
    tab_bg.draw.rect((0,0,0,200),[0,60,700,350],5,10)
    tab_bg.blit(tab_text,(400-(tab_text.size[0]/2)-50,10))
    tab_a = -1000
    isTab = False

    isEscape = False

    run = True
    while run:
        for event in pygwin.getEvents():
            if event.type == pygwin.QUIT:
                run = False
            elif event.type == pygwin.KEYUP:
                if event.key == pygwin.K_TAB:
                    isTab = isTab != 1
                    if isTab: isEscape = False
                if event.key == pygwin.K_ESCAPE:
                    if isTab:
                        isTab = False
                    else:
                        isEscape = isEscape != 1
                if event.key == pygwin.K_p:
                    import game
                    game.Game(False,preview=True,blocks=[i.__dict__()for i in blocks]).start()
                    raise SystemExit

        win.fill((25,25,25))
        win.blit(blocks_surface,(0,0))

        if isEscape:
            win.blit(escape_bg,(escape_a,0))
            if escape_a > 0:
                escape_a -= escape_a/10
            if tab_a > -1000:
                tab_a -= (1000+tab_a)/10
                win.blit(tab_bg,(50+tab_a,50))
            pos = pygwin.mouse.gpos()

            load_text_center = (escape_a+escape_rect_1.x+escape_rect_1.w/2-load_text.size[0]/2,
                                escape_rect_1.y+escape_rect_1.h/2-load_text.size[1]/2)
            if escape_rect_1.contains(*pos):
                win.blit(load_text_active,load_text_center)
                if pygwin.mouse.isPressed("left"):
                    tk = Tk()
                    tk.withdraw()
                    f = filedialog.askopenfilename(initialdir="/",title="Загрузить карту",
                               filetypes=(("Cubit файлы","*.cubit"),("All files","*.*")))
                    if f != None and f != "":
                        blocks = map.map_load(f)
                    tk.destroy()
                    update_blocks()
            else:
                win.blit(load_text,load_text_center)


            save_text_center = (escape_a+escape_rect_2.x+escape_rect_2.w/2-save_text.size[0]/2,
                                escape_rect_2.y+escape_rect_2.h/2-save_text.size[1]/2)
            if escape_rect_2.contains(*pos):
                win.blit(save_text_active,save_text_center)
                if pygwin.mouse.isPressed("left"):
                    tk = Tk()
                    tk.withdraw()
                    f = filedialog.asksaveasfilename(initialdir="/",title="Сохранить карту",
                                filetypes=(("Cubit файлы","*.cubit"),("All files","*.*")),defaultextension=".cubit")
                    if f != None and f != "":
                        map.map_dump(blocks,f)
                    tk.destroy()
            else:
                win.blit(save_text,save_text_center)

            escape_text_center = (escape_a+escape_rect_3.x+escape_rect_3.w/2-escape_text.size[0]/2,
                                  escape_rect_3.y+escape_rect_3.h/2-escape_text.size[1]/2)
            if escape_rect_3.contains(*pos):
                win.blit(escape_text_active,escape_text_center)
                if pygwin.mouse.isPressed("left"):
                    import main
                    main.main()
                    raise SystemExit
            else:
                win.blit(escape_text,escape_text_center)

            if not escape_rect.contains(*pos):
                if pygwin.mouse.isPressed("left"):
                    isEscape = False

        elif isTab:
            win.blit(tab_bg,(50+tab_a,50))
            if tab_a < 0:
                tab_a += tab_a*-1/10
            if escape_a < 1000:
                escape_a += (1000-escape_a)/10
                win.blit(escape_bg,(escape_a,0))

            p = pygwin.mouse.gpos()

            inv = list(inventory.items())

            i = 0
            for y in range(5):
                for x in range(10):
                    r = pygwin.rect(50+x*70+tab_a,110+y*70,70,70)
                    if r.contains(*p):
                        win.draw.rect((100,100,100,128),r,0,10)
                        if pygwin.mouse.isPressed("left"):
                            localBlockType = inv[i][0]
                    if localBlockType == inv[i][0]:
                        win.draw.rect(inv[i][1][0],
                          [r.x+10,r.y+10,50,50])
                    else:
                        win.draw.rect(inv[i][1][0],
                          [r.x+20,r.y+20,30,30])
                    i += 1
                    if i >= len(inv): break
                if i >= len(inv): break

            i = 0
            for y in range(5):
                for x in range(10):
                    r = pygwin.rect(50+x*70+tab_a,110+y*70,70,70)
                    if r.contains(*p):
                        t = data.font.render(inv[i][1][1],20,(200,200,200))
                        tr = t.rect(p[0],p[1])
                        win.draw.rect((50,50,50),[tr.x,tr.y-30,tr.w+10,tr.h+10])
                        win.draw.rect((20,20,20),[tr.x,tr.y-30,tr.w+10,tr.h+10],2)
                        win.blit(t,(p[0]+5,p[1]-25))
                    i += 1
                    if i >= len(inv): break
                if i >= len(inv): break
        else:
            if tab_a > -1000:
                tab_a -= (1000+tab_a)/10
                win.blit(tab_bg,(50+tab_a,50))
            if escape_a < 1000:
                escape_a += (1000-escape_a)/10
                win.blit(escape_bg,(escape_a,0))

            p = [pygwin.mouse.gpos()[0]//16*16,
                 pygwin.mouse.gpos()[1]//16*16]

            if pygwin.mouse.isPressed("left"):
                delete_block(p)
            elif pygwin.mouse.isPressed("right"):
                create_block(p,localBlockType)
            s = pygwin.surface((16,16))
            s.fill((*inventory[localBlockType][0],64))
            win.blit(s,p)

        win.update(120)

if __name__ == '__main__':
    main()
