import os
import socket
import threading
import time
import pygame.camera

from DH import *
from cryptography.hazmat.backends import default_backend
from Compress import Compress
from Watermarking import *
from enc import encrypt_image
from dec import decrypt_image




class Server():


    def __init__(self):
        self.port = 5555
        self.ip_address = "192.168.1.103" #socket.gethostbyname(socket.gethostname())
        self.name = socket.gethostname()
        self.format = "UTF-8"
        self.disconnect_msg = "#DIS"
        self.address = (self.ip_address,self.port)
        self.header = 2048
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clients = []
        self.image_num = 0
        self.authenticate(self.server)

    def init_Server(self):
        self.server.bind(self.address)
        print(f"[SERVER]Initisializing Server {self.address[0]}")
        self.server.listen()
        print("[Server]Server Initialised Successfully!")
        thread = threading.Thread(target=self.add_client)
        thread.start()
    

    def add_client(self):
        

        while True:
            conn,addrs = self.server.accept()
            if conn not in self.clients:
                self.clients.append(conn)
                print(f"[SERVER] {self.clients.__len__()} Active Connections.")
                threading.Thread(target=self.recieve_msg,args=[conn]).start()
            

    
    def key_exchange(self,conn:socket.socket) -> bytes:
        try:
            for i in range(3):
                
                    key_generate = DH()
                
                    key_generate.generate_dh_key_pair()
                    public_server = key_generate.generate_dh_key_pair()

                    print("[SERVER]sending public key to client!")
                    
                    conn.send(public_server)
                    client_public = conn.recv(self.header)
                    return key_generate.compute_shared_secret(client_public)
            x = 0
        
            
            return x.to_bytes()
        except Exception as err:
            print(f"[SERVER]Error happened {err}")
            x = 0
            return x.to_bytes()

    def authenticate(self,conn:socket.socket) -> bool:
        global key
        key = self.key_exchange(conn)
        
        print(f"[Server]key:{key} ")
        if key == 0:
            return False
        else:
            
            return True

    def recieve_msg(self,conn:socket.socket):

        if not self.authenticate(conn):
            return

        while True:
            try:
                    if (conn):
                        msg_length = conn.recv(self.header).decode(self.format)
            
                        if msg_length:
                            #msg_length = int(msg_length)
                            #msg = self.clients[0].recv(msg_length.__len__()).decode(self.format)
                            #msg = self.clients[0].recv(self.header).decode(self.format)
                            print(f"[Client:{conn.getsockname()[0]}] {msg_length}")

            except Exception as err:
                print(f"[SERVER]Error Client[{conn.getsockname()[0]}] Connection lost ending socket in 5s....")
                
                try:
                        conn.close()
                        self.clients.remove(conn)
                        break
                except Exception as ERR:
                        print(ERR)
                        

        time.sleep(5)


    def send_message(self,socket:int,msg:str):
            try:
                msg.encode(self.format)
                msg_length = len(msg)
                send_length = str(msg_length).encode(self.format)
                send_length += b' ' * (self.header - len(send_length))               
                self.clients[socket].send(msg.encode(self.format))
            except Exception as err:
                print(f"[SERVER]Error happened couldn't send message!")


    def send_img(self,path:str,client_num:int):
        try:
            try:
                file = open(f"{path}","rb")
                image_chunk = file.read(self.header)

            except:
                print("[SERVER]Couldn't read file please try again!")
                
            if image_chunk:
                print("[SERVER]Sending image....")

            try:
                while image_chunk :
                    self.clients[client_num].send(image_chunk)
                    image_chunk = file.read(self.header)
                    
                self.clients[client_num].send("IMAGE_DONE".encode(self.format))
                print("[SERVEER]Transmission complete.")

                file.close()
            except:
                print(f"[SERVER]Error Couldn't send image to client:{client_num}")
        except:
            print("[SERVER]Error couldn't send file!")
            print("[SERVER]Please Try again in 5s")
            time.sleep(5)

    def send_file(self,path):
        CHUNKSIZE = 1_000_000
        filename = path
        f = open(filename,'rb') 
        self.clients[0].sendall(filename.encode() + b'\n')
        self.clients[0].sendall(f'{os.path.getsize(filename)}'.encode() + b'\n')

    # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(CHUNKSIZE)
            if not data: break
            self.clients[0].sendall(data)
        f.close()



s = Server()
s.init_Server()
pygame.camera.init()
camlist = pygame.camera.list_cameras()









while True:

    if camlist:
    
        # Initialize and start camera  
        cam = pygame.camera.Camera(camlist[0], (640, 480))
        cam.start()
        
        # capturing the single image
        image = cam.get_image()
        
        # saving the image
        pygame.image.save(image, "filename.png")
        cam.stop()
    else:
        print("Error Camera not found!")

    Compress("filename.png","filename.png")
    wm = Watermarking("filename.png","filename.png",key)
    wm.embed_watermark()
    encrypt_image("filename.png","filenameEnc.png",key)
    s.send_file("filenameEnc.png")
    s.send_file("filename.png.iv")