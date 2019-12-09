'''
Author : Luis H 
        Sebastian V
'''
import zmq
import os
import json
import hashlib

ctx = zmq.Context()
FILES = os.listdir(os.getcwd()+"/provider")
CANT = 1024*1024

def hashBytes(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    sha.update(s)
    return sha.hexdigest()

def uploadParts(conexion):

    for archive in FILES:
        DIC = {}    
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
                    hashContent = hashBytes(content) #nombre para guardar
                    LISTAPARTES.append(hashContent)
                    hashContentInt = int(hashContent, 16)  % (1024*1024*1024 ) #reducir de 2²⁵⁶-1  a 2²⁰-1 
                                                                              # numero maximo es 1073741823
                    s = {
                        "request": "upload",
                        "id": hashContentInt,
                        "name": hashContent,
                        "bytes": content
                    }
                    
                    dir = "127.0.0.1" + ":" + "5555"
                    a = False
                    #Envio de la parte del archivo
                    while a == False: 
                        conexion.connect("tcp://"+ dir)
                        conexion.send_pyobj(s) 
                        m = conexion.recv_pyobj()
                        if m['reply'] == True:
                            a == True
                            break
                        else:
                            conexion.disconnect("tcp://"+ dir)
                            dir = m["nextIp"]
                            
                    conexion.disconnect("tcp://"+ dir)
                    
        DIC[archive] = LISTAPARTES        
        dicString = json.dumps(DIC)
        
        with open(archive.split(".")[0]+".chord","w") as f:
            f.write(dicString)
            f.close()
        
        print("repartido!!!")

conexion = ctx.socket(zmq.REQ)
uploadParts((conexion))

