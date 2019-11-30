import zmq
import os
import json
import hashlib

ctx = zmq.Context()
FILES = os.listdir(os.getcwd()+"/provider")
CANT = 1024*1024
DIC = {}

conexion = ctx.socket(zmq.REQ)

def hashBytes(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    sha.update(s)
    return sha.hexdigest()

def uploadParts(conexion):
    global DIC
    variable = 0
    for archive in FILES:    
        LISTAPARTES = []
        print("------------")
        print("cancion {}".format(archive))
        with open('provider/'+ archive,'rb') as f:    
            while True:
                content = f.read(CANT)
                #content es una parte en bytes del archivos
                if not content:
                    break
                else:
                    hashContent = hashBytes(content)
                    LISTAPARTES.append(hashContent)
                    hashContentInt = int(hashContent, 16) % (1024*1024*1024) #reducir de 2²⁵⁶-1  a 2²⁰-1 
                    #print(hashContentInt)
                    
                    # Dictionary m to send
                    _ = input("espere .. nueva parte")
                    
                    s = {
                        "request": "upload",
                        "id": variable,#hashContentInt,
                        "name": hashContent
                        #"content": content
                    }
                    print("id : {}".format(hashContentInt))
                    
                    dir = "192.168.0.4" + ":" + "5555"
                    a = False
                    while a == False: 
                        conexion.connect("tcp://"+ dir)
                        conexion.send_json(s) 
                        m = conexion.recv_json()
                        if m['reply'] == True:
                            a == True
                            variable+=1
                            conexion.send_multipart([content])
                            _ = conexion.recv_string()
                            break
                        else:
                            conexion.disconnect("tcp://"+ dir)
                            dir = m["nextIp"]
                            
                    
                    conexion.disconnect("tcp://"+ dir)
                    
        DIC[archive] = LISTAPARTES        
        print("repartido!!!")
uploadParts((conexion))
#print (DIC)  