import zmq
import os
import json
import hashlib

ctx = zmq.Context()

FILES = os.listdir(os.getcwd()+"/provider")

CANT = 1024*1024*2

DIC = {}


def hashBytes(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    return sha.hexdigest()

def upload_parts():

    
    for song in FILES:

        LISTAPARTES = []

        with open('provider/'+song,'rb') as f:
                
            while True:
                
                content = f.read(CANT)
                if not content:
                    break
                else:
                    hashContent = hashBytes(content)
                    LISTAPARTES.append(hashContent)
                    hashContentInt = (int(hashContent, 16) % (1024 * 1024))
                    # DIctionary m to send
                    m = {
                        "id": hashContentInt,
                        "name": hashContent,
                        "content": content
                    }
                    
                    #send m CICLO DE ENVIO PAPUDEPAPUS
                    
        DIC[song] = LISTAPARTES        
        
upload_parts()
print (DIC)  

