import os
import json
import zmq
import hashlib

ctx = zmq.Context()
CANT = 1024*1024

def hashBytes(s):
    # Recibe una cadena y calcula el sha256
    sha = hashlib.sha256()
    sha.update(s)
    return sha.hexdigest()

def uploadFile(conexion):
    os.system("clear")
    archive = input("Upload File")

    DIC = {}    
    LISTAPARTES = []
    with open(archive,'rb') as f:    
        while True:
            content = f.read(CANT)
            #content es una parte en bytes del archivos
            if not content:
                f.close()
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
                
                #Envio de la parte del archivo
                while True: 
                    conexion.connect("tcp://"+ dir)
                    conexion.send_pyobj(s) 
                    m = conexion.recv_pyobj()
                    if m['reply'] == True:
                        break
                    else:
                        conexion.disconnect("tcp://"+ dir)
                        dir = m["nextIp"]
                            
                conexion.disconnect("tcp://"+ dir)

        f.close()    
        DIC[archive] = LISTAPARTES        
    
    dicString = json.dumps(DIC)
    print("archivo es {}  cpm tipo {}".format(archive,type(archive)))
    with open(archive.split(".")[0]+".chord","w") as f:
        f.write(dicString)
        f.close()
        
    print("Archivo Subido a la Red!!!\n Magnet Link Generado")
    _ = input("PRESS <<ENTER>> TO CONTINUE")

def downloadFile(conexion):
    os.system("clear")
    a = input("Ingrese el nombre del archivo magnet link\n")
    jsonDat = None
    try: 

        with open(a,"r") as file:
            content = file.read()
            jsonDat = json.loads(content)
            print(jsonDat)
            file.close()
        # Descarga de archivo y guardar archivo local 
        byteList = []
        name = None
        # Saco el nombre del archivo
        for k in jsonDat.keys():
            name = k

        files = jsonDat[k]

        with open(name,"ab") as file:
            for i in files:
                dir = "127.0.0.1" + ":" + "5555"
                # Recepción de la parte del archivo
                while True:

                        s = { "request" : "download",
                              "id"   : 0,
                              "name" : i

                        } 
                        conexion.connect("tcp://"+ dir)
                        conexion.send_pyobj(s) 
                        m = conexion.recv_pyobj()
                        if m['reply'] == True:
                            file.write(m["file"])
                            conexion.disconnect("tcp://"+ dir)
                            break
                        else:
                            conexion.disconnect("tcp://"+ dir)
                            dir = m["nextIp"]
            file.close()
        print("ARCHIVO DESCARGADO!!")
      
          
    except:
        print("Error ")

    _ = input("PRESIONE <<ENTER>> PARA CONTINUAR")

def menu():
    conexion = ctx.socket(zmq.REQ)
    op = -1
    while(int(op) < 3):
        os.system('clear')    
        print("_____________________________________________________")
        print("|                   W E L C O M E                   |")
        print("|                                                   |")
        print("|                  1: Upload File                   |")
        print("|                  2: Download File                 |")
        print("|                  3: Exit                          |")
        print("|___________________________________________________|")
        op = input(" Please, select one option: ")
        os.system('clear')
        if(op == "1"):       
            uploadFile(conexion)
        elif(op == "2"):
            downloadFile(conexion)
        else:
            print ("Exit!")

menu()