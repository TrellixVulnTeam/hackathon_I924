
import time
from socket import *
import struct
import colorama
import os

# Windows
if os.name == 'nt':
    import msvcrt
    import sys

# Posix (Linux, OS X)
else:
    import sys
    import select
    import tty
    import termios


class Client:

    def __init__(self, name):
        self.name = name
        colorama.init()
        print(f'{colorama.Fore.GREEN}Client started, listening for offer requests...')

    def look_for_server(self):
        '''method for looking for a server, the client recives
        udp packets and if the packets is offer from  a server
        the client connects to the server'''
        magic_cookie = 4276993775
        port = 13117
        msg = 0
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_socket.bind(('', port))
        while msg != magic_cookie:
            data,adrr = udp_socket.recvfrom(1024)
            try:
                data = struct.unpack("Ibh", data)
            except:
                continue
            print(f'{colorama.Fore.LIGHTYELLOW_EX}Received offer from ' + f'{colorama.Fore.LIGHTYELLOW_EX}' + str(adrr[0]) + f'{colorama.Fore.LIGHTYELLOW_EX} ,attempting to connect...')
            if data[0] == magic_cookie:
                msg = magic_cookie
            else:
                print(f'{colorama.Fore.RED}connection failed, trying again')
        udp_socket.close()
        return data[2], adrr[0]

    def connect_to_server(self, address):
        "method for set up the connection with the server"
        try:
            tcp_Socket = socket(AF_INET, SOCK_STREAM)
            tcp_Socket .setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            tcp_Socket .connect((address[1], address[0]))
            tcp_Socket .send(str.encode(self.name + "\n"))
            return tcp_Socket
        except:
            print(colorama.Fore.RED+"connection failed")
            return

    def communicate_with_server(self, socket):
        '''method for the communication with the server during the game,
        the client send the server the characters pressed from the key board
        and recive messages during the game'''
        try:
            msg = socket.recv(1024)
        except:
            print(colorama.Fore.RED+"connection lost, listening for offer requests...")
            try:
                socket.close()
                return
            except:
                return
        msg = msg.decode(encoding="utf-8")
        print(msg)
        t_end = time.time() + 10
        while time.time() < t_end:
            if os.name == 'nt':
                try:
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        socket.send(str.encode(key.decode(encoding='utf-8')))
                except:
                    print("connection lost, listening for offer requests...")
                    return
            else:
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    if self.isData():
                        c = sys.stdin.read(1)
                        socket.send(str.encode(c))
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        try:
            msg = socket.recv(1024)
        except:
            print(f'{colorama.Fore.RED}connection lost, listening for offer requests...')
            socket.close()
            return
        msg = msg.decode(encoding="utf-8")
        print(f'{colorama.Fore.CYAN}' + msg)
        socket.close()
        print("Server disconnected, listening for offer requests...")

    def isData(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])





def run_client(client):
    '''driver code for the client'''
    while True:
        addr = client.look_for_server()
        socket = client.connect_to_server(addr)
        if socket is None:
            continue
        client.communicate_with_server(socket)
        time.sleep(0.1)


c = Client("STUXNET")
run_client(c)
