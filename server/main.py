from socket import socket as Socket, timeout
from threading import Thread
from data.data import *
import time

# client -> server {'name':name,'password':password,'version':version}
# server -> client {'done':placeable} or {'error':error}
# client -> server {'move':{
#                     'left',
#                     'right',
#                     'jump'
#                  }, 'block':{
#                      'delete':{
#                          'pos':[x,y],
#                          'type':type},
#                      'create':{
#                          'pos':[x,y],
#                          'type':type}
#                      }
#                  }
# server -> client {'players':{name:[x,y]},'blocks':[{'pos':[x,y],'type':type}]}

class Server:
    def __init__(self):
        self.conf = yaml.load("data/config.yaml")

        self.socket = Socket()
        self.socket.bind((self.conf["address"],
                          self.conf["port"]))
        self.socket.listen(5)

        self.run = True
        self.users = {}
        self.fps = 1/60


        self.editable = self.conf["editable"]
        self.protocol = self.conf["protocol"]
        self.world = World(self,speed=self.conf["speed"],
                           gravity=self.conf["gravity"])
        Thread(target=self.world.update,daemon=True).start()

        self.accept()

    def user(self,conn,address):
        address = f'{address[0]}:{address[1]}'
        conn.settimeout(1)

        try: data = conn.recv(1024*40)
        except: return

        def close():
            try: conn.close()
            except: pass

        def send(data):
            try: conn.send(pickle.dumps(data))
            except: pass

        def send_error(text):
            send({'error':str(text)})
            time.sleep(1)
            close()

        def blocknear(player,block,radius=160):
            br = [block.pos[0]-radius/2,
            block.pos[1]-radius/2,radius,radius]
            for x in range(br[2]):
                x += br[0]
                for y in range(br[3]):
                    y += br[1]
                    if x == player.pos[0]:
                        if y == player.pos[1]:
                            return True
            return False

        try:
            data = pickle.loads(data)
        except:
            log(f'???? ?????????????? ?????????????? ???????????? ???? {name}-{address}.')
            return send_error('???? ?????????????? ?????????????? ????????????.')

        if [*data.keys()] != ['name','password', 'version']:
            log(f'?? {name}-{address} ???????????????????????? ?????????? ?????????? ?? ????????????.')
            return send_error('???????????????????????? ?????????? ?????????? ?? ????????????.')

        name = str(data['name'])
        password = str(data['password'])
        version = str(data['version'])

        try:
            player = self.world.create_player(name,password)
            if self.editable:
                send({'editable':self.editable})
            else:
                send({'editable':self.editable,
                      'blocks':map.map_dumps(self.world.blocks)})
        except Exception as e:
            return send_error(e)

        log(f'{address} ?????????????????????? ?????? {name}')
        conn.settimeout(5)
        while True:
            if(version != self.protocol):
                break
            try:
                data = conn.recv(1024*40)
                data = pickle.loads(data)
            except timeout:
                send_error('?????????? ???????????????? ??????????')
                log(f'?? {name}-{address} ?????????? ?????????? ????????????????.')
                break
            except ConnectionResetError:
                break
            except EOFError:
                pass
            else:
                if isinstance(data,dict):
                    if 'move' in data and isinstance(data['move'],dict):
                        if data['move']['x'] == 'left':
                            player.sx = -self.world.speed

                        if data['move']['x'] == 'right':
                            player.sx = self.world.speed

                        if data['move']['y'] == 'jump':
                            if player.collision or player.y == 496: player.sy = -8

                    if 'respawn' in data:
                        player.pos = copy.copy(self.world.start)
                        player.speed = [0,0]
                        player.collision = False

                    if self.editable:
                        if 'block' in data.keys():
                            if 'delete' in data['block']:
                                b = block(
                                data['block']['delete']['pos'],
                                data['block']['delete']['type'])
                                if blocknear(player,b):
                                    self.world.pop_block(b)
                            if 'create' in data['block']:
                                b = block(
                                data['block']['create']['pos'],
                                data['block']['create']['type'])
                                if blocknear(player,b):
                                    self.world.add_block(b)

                    if 'ping' in data:
                        send({'ping':time.time()})

                if not self.editable:
                    send({'players':self.world.get_players()})
                else:
                    send({'players':self.world.get_players(),
                          'blocks':map.map_dumps(self.world.blocks)})
            time.sleep(self.fps)
        self.world.pop_player(player)
        log(f'{name} ????????????????????...')

    def accept(self):
        while True:
            conn, address = self.socket.accept()
            Thread(target=self.user,daemon=True,args=(conn,address)).start()

if __name__ == '__main__':
    Server()
