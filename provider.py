import zmq
import os
import json

ctx = zmq.Context()

FILES = os.listdir(os.getcwd()+"/provider")

CANT = 1024*1024*2

def upload_parts():

    DIC = {}
    
    for song in FILES:

        LISTAPARTES = []

        with open('provider/'+song,'rb') as f:
                
            while True:
                
                content = f.read(CANT)
                if not content:
                    break
                else:
                    #calculo hash a la parte (content) HashCont
                    #LISTAPARTES.append(HashContent)

                    
        DIC[song] = LISTAPARTES        

   
print(FILES)

