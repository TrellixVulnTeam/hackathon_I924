import select
import time
from socket import *
import struct
from msvcrt import getch
from msvcrt import kbhit


class Client:

    def __init__(self, name):
        self.name = name
        #self.udp_client_Socket = socket(AF_INET, SOCK_DGRAM)
        #self.tcp_client_Socket = socket(AF_INET, SOCK_STREAM)
        print("Client started, listening for offer requests...")

    def look_for_server(self):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_socket.bind(('', 13117))
        magic_cookie = 4276993775
        msg = 0
        while msg != magic_cookie:
            data,adrr = udp_socket.recvfrom(1024)
            data = struct.unpack("Ibh", data)
            print("Received offer from " + adrr[0] + " ,attempting to connect...")
            if data[0] == magic_cookie:
                msg = magic_cookie
            else:
                print("connection failed, trying again")
        udp_socket.close()
        return data[2], adrr[0]

    def connect_to_server(self, address):
        try:
            tcp_Socket = socket(AF_INET, SOCK_STREAM)
            tcp_Socket .setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            tcp_Socket .connect((address[1], address[0]))
            tcp_Socket .send(str.encode(self.name + "\n"))
            return tcp_Socket
        except:
            print("connection failed")

    def communicate_with_server(self, socket):
        try:
            msg = socket.recv(1024)
        except:
            print("connection lost, listening for offer requests...")
            socket.close()
            return
        msg = msg.decode(encoding="utf-8")
        print(msg)
        #self.tcp_client_Socket.settimeout(0.001)
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                if kbhit():
                    key = getch()
                    socket.send(str.encode(key.decode(encoding='utf-8')))
            except:
                print("connection lost, listening for offer requests...")
                return
        try:
            msg = socket.recv(1024)
        except:
            print("connection lost, listening for offer requests...")
            socket.close()
            return
        msg = msg.decode(encoding="utf-8")
        print(msg)
        socket.close()
        print("Server disconnected, listening for offer requests...")


def run_client(client):
    while True:
        addr = client.look_for_server()
        s = client.connect_to_server(addr)
        client.communicate_with_server(s)


c = Client("Santa Claus")
run_client(c)