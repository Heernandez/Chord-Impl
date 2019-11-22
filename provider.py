import zmq
import os
import json

ctx = zmq.Context()

SERVERS = []

FILES = os.listdir(os.getcwd()+"/provider")

CANT = 1024*1024*2

SENT = {}

def add_servers():
    global SERVERS
    s   = ctx.socket(zmq.REQ)
    s.connect("tcp://localhost:6000") 
    
    s.send_multipart([b'90'])
    m = s.recv_multipart()

    for i in m:
        SERVERS.append(i.decode('utf-8'))
    
    print("listado de servidores listo")

def upload_parts():
    global SERVERS
    global SENT
            
    
    
    for song in FILES:
        
        print("voy a enviar la cancion :",song)
        
        namePart = ''
        portListOrder = []       
        portCant = len(SERVERS)          
        i = 0
        iter = 1
        
        with open('provider/'+song,'rb') as f:
                
            while True:
                
                content = f.read(CANT)
                
                if not content:
                    break
                else:
                    #partir con os.path.splittext()  [pos 0]
                    
                    namePart = os.path.splitext(song)[0]+str(iter)
                                        
                    portAsign = SERVERS[i]

                    print("la parte ",namePart," se guarda en el servidor :",portAsign)
                    
                    s   = ctx.socket(zmq.REQ)
                    s.connect("tcp://localhost:"+portAsign)
                    s.send_multipart([ b'cancion',namePart.encode(),content])
                    bash = s.recv_multipart()              
                
                portListOrder.append(portAsign)
                
                iter +=1
                
                if i == (portCant - 1):
                    i = 0
                else:
                    i+=1

            SENT[song] = portListOrder          

def send_register():
    s   = ctx.socket(zmq.REQ)
    s.connect("tcp://localhost:6000") 

    s.send_json(SENT)
    
    a = s.recv_multipart()
    
    print("confiman ",a[0].decode('utf-8'))
    print (SENT)
   


add_servers()
upload_parts()
send_register()


