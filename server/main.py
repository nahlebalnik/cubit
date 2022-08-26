from socket import socket as Socket, timeout
from threading import Thread
from data.data import *

# client -> server {'name':name,'password':password,'version':version}
# server -> client {'done':None} or {'error':error}
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
    def __init__(self,port):
        self.socket = Socket()
        self.socket.bind(('localhost',port))
        self.socket.listen(5)

        self.run = True
        self.users = {}
        self.fps = 1/60

        self.actualVersion = '2.1'

        self.world = World(self,speed=2,gravity=1)
        Thread(target=self.world.update,daemon=True).start()

        self.accept()

    def user(self,conn,address):
        address = f'{address[0]}:{address[1]}'
        conn.settimeout(1)

        try: data = conn.recv(1024)
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
            log(f'Не удалось принять данные от {name}-{address}.')
            return send_error('Не удалось принять данные.')

        if [*data.keys()] != ['name','password', 'version']:
            log(f'У {name}-{address} неправильная форма имени и пароля.')
            return send_error('Неправильная форма имени и пароля.')

        name = str(data['name'])
        password = str(data['password'])
        version = str(data['version'])

        try:
            player = self.world.create_player(name,password)
            send({'done':None})
        except Exception as e:
            return send_error(e)

        log(f'{address} подключился как {name}')
        conn.settimeout(5)
        while True:
            if(version != self.actualVersion):
                break
            try:
                data = conn.recv(1024)
                data = pickle.loads(data)
            except timeout:
                send_error('Время ожидания вышло')
                log(f'У {name}-{address} вышло время ожидания.')
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

                send({'players':self.world.get_players(),
                      'blocks':self.world.get_blocks()})
            time.sleep(self.fps)
        self.world.pop_player(player)
        log(f'{name} отключился...')

    def accept(self):
        while True:
            conn, address = self.socket.accept()
            Thread(target=self.user,daemon=True,args=(conn,address)).start()

if __name__ == '__main__':
    Server(12000)
