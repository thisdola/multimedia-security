import socket
import threading
import time
import os
from DH import DH
from cryptography.hazmat.backends import default_backend

from dec import decrypt_image
from detect_and_remove import DetectAndRemove


image_num = 1

class Client():
    def __init__(self,server_ip,port,msg_size=2048,encodingformat="UTF-8"):
        self.HEADER = msg_size
        self.FORMAT = encodingformat
        self.SERVER = server_ip
        self.PORT = port
        self.DISCONNEC_MSG = "#DISCONNECT"
        self.ADDR = (self.SERVER,self.PORT)
        RECV = False
        self.client  = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_state = False

    def set_state(self,state:bool):
        self.client_state = state

    def get_state(self)->bool:
        return self.client_state

    def start(self):
        while not self.get_state():
            try:
                self.client.connect(self.ADDR)

                print(f"[{socket.gethostname()}]")
                if not self.authenticate():
                    self.client.close()
            except Exception as Error:
                print(f"[{socket.gethostname()}]Error couldn't connect to server {Error}")
                time.sleep(5)

            else:
                self.set_state(True)
                print(f"[{socket.gethostname()}]Server {self.SERVER} connected successfully!")


    def authenticate(self) -> bool:

        try:
            print()
            key_generate = DH()
            client_pubKey = key_generate.generate_dh_key_pair()
            server_pubKey = self.client.recv(2048)
            self.client.send(client_pubKey)
            
            self.dh_key = key_generate.compute_shared_secret(server_pubKey)
            print(self.dh_key)
        except Exception as err:
            print(f"[{socket.gethostname()}Error happened while authenticating Server]")
            return False
        
        else:
            print(f"[{socket.gethostname()}]Server authenticated successfully!")
            return True
        

    def send(self,msg):
        try:
            message = msg.encode(self.FORMAT)
            #msg_length = len(message)
            #send_length = str(msg_length).encode(FORMAT)
            #send_length += b' ' * (HEADER - len(send_length))
            #client.send(send_length)
            self.client.send(message)
        except  Exception as Error:
            print(f"[{socket.gethostname()}]Error couldn't send to server! {Error}")
            self.client.close()
            self.set_state(False)
            time.sleep(5)


            

    def recieve(self):
        while True:
            try:
                if self.get_state():
                    
                    try:
                        MSG = self.client.recv(2048).decode(self.FORMAT)
                    except Exception as err:
                        if err == TimeoutError:
                            pass
                        else:
                            print(f"[{socket.gethostname()}]Error:{err}")
                    
                    if MSG:
                        print(f"[Client:{self.client.getsockname()[0]}]{MSG}")
                        return MSG
                    if MSG.strip() == self.DISCONNEC_MSG:
                        self.client.close()
                        print(f"[{socket.gethostname()}] Server Disconnected!")

            except:
                print(f"[{socket.gethostname()}]Error Couldn't recieve from server")
                time.sleep(5)
                self.set_state(False)
                

    def recv_file(self,name:str,extention:str):
            global image_num
            try:   
                self.client.settimeout(2)
                try:
                    image_chunk = self.client.recv(self.HEADER)
                except:
                    image_chunk = 0
                    return False
                
                Event = threading.Event()
                Event.set()
                if image_chunk:
                    print(f"[{socket.gethostname()}]recieving image.......")
                    file = open(f"{name}{image_num}.{extention}","wb")
                    while image_chunk and self.client.recv(self.HEADER):
                        file.write(image_chunk)
                        try:
                            image_chunk = self.client.recv(self.HEADER)
                        except:
                            break
                        
                    
                    file.close()
                    print(f"[{socket.gethostname()}]Image recieved!")
                    image_num+=1
                    
                Event.clear()
                
            except Exception as err:
                print(f"[{socket.gethostname()}]Error:{err}")
                return False
            else:
                return True
            

    def recieve_file(self)->bool:


        CHUNKSIZE = 1_000_000

        # Make a directory for the received files.
        os.makedirs('Downloads',exist_ok=True)      
        while True:
                

                # Use a socket.makefile() object to treat the socket as a file.
                # Then, readline() can be used to read the newline-terminated metadata.
                    clientfile = self.client.makefile('rb')
                    filename = clientfile.readline().strip().decode()
                    length = int(clientfile.readline())
                    print(f'Downloading {filename}:{length}...')
                    path = os.path.join('Downloads',filename)

                    # Read the data in chunks so it can handle large files.
                    with open(path,'wb') as f:
                        while length:
                            chunk = min(length,CHUNKSIZE)
                            data = clientfile.read(chunk)
                            if not data: break # socket closed
                            f.write(data)
                            length -= len(data)

                    if length != 0:
                        print('Invalid download.')
                        return False
                    else:
                        print('Done.')
                        return True

client = Client("192.168.1.103",5555)

client.start()

i = 0
while True:
    
    client.recieve_file()
    client.recieve_file()
    decrypt_image("Downloads/filenameEnc.png","Downloads/filenameDec.png",client.dh_key,"Downloads/filename.png.iv")
    wm = DetectAndRemove("Downloads/filenameDec.png",client.dh_key,"Downloads/filenameDec.png")
    wm.check_watermark()
    