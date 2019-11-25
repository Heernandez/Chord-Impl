import zmq
import os
import json
import hashlib

ctx = zmq.Context()
FILES = os.listdir(os.getcwd()+"/provider")
CANT = 1024*1024*2
DIC = {}

conexion = ctx.socket(zmq.REQ)

def hashBytes(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    return sha.hexdigest()

def uploadParts(conexion):
    global DIC
    for archive in FILES:    
        LISTAPARTES = []
        with open('provider/'+ archive,'rb') as f:    
            while True:
                content = f.read(CANT)
                if not content:
                    break
                else:
                    hashContent = hashBytes(content)
                    LISTAPARTES.append(hashContent)
                    hashContentInt = (int(hashContent, 16) % (1024 * 1024)) #reducir de 2²⁵⁶-1  a 2²⁰-1 
                    # Dictionary m to send
                    s = {
                        "request": "upload",
                        "id": hashContentInt,
                        "name": hashContent,
                        "content": content
                    }
                    dir = "10.253.2.201" + ":" + "5555"
                    a = False
                    while a == False: 
                        conexion.connect("tcp://"+ dir)
                        conexion.send_json(s) 
                        m = conexion.recv_json()
                        if m["reply"] == True:
                            a == True
                        else:
                            conexion.disconnect("tcp://"+ dir)
                            dir = m["nextIp"]
                    
        DIC[archive] = LISTAPARTES        
        
uploadParts((conexion))
print (DIC)  
'''
DIC = { "ARCHIVO1": [DWJFEIGJE,EBTRTRYN,RTHTYJTYJ],
        .....
         "ARCHIVON": [DWJFEIGJE,EBTRTRYN,RTHTYJTYJ],




}
'''