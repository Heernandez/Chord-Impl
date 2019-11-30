import zmq
import os
import socket as sk
import hashlib
import random
import string
ctx = zmq.Context()


def hashName(id):
    # Recibe la ip concatenada con una cadena aleatoria de 25 caracteres y devuelve el hash
    sha = hashlib.sha256()
    sha.update(id.encode('ascii'))
    return sha.hexdigest()

def generation(ip, size = 25):
    # Recibe una ip y le concatena una cadena aleatoria de 25 caracteres
    answer = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                      for x in range(size))
    attempt = ip + answer
    hashN = hashName(answer)
    hashInt = int(hashN, 16) % (1024*1024*1024)
    return hashInt

PATH = ""
MYLIST = []

class Peer:

    def __init__(self):
        
        # Id del nodo
        
        self.myIp = self.getIp()
        self.id = generation(self.myIp)
        #Define los limites de resposabilidad, R[0] Lim Inferior , R[1] Lim Superior (es el mismo id)
        
        self.R = [self.id + 1,self.id]
        #self.R = [1073741823,1073741822 - 1]

        # Sockets del peer
        self.socketClient = ctx.socket(zmq.REP)
        self.socketPredecessor = ctx.socket(zmq.REP)
        self.socketSuccessor = ctx.socket(zmq.REQ)
        
        self.portClient =      "8555"  #5555    7777    7007
        self.portPredecessor = "8000"  #4444    8888    8008
        self.portSuccessor =   "8000"  #4444    8888    8008

        self.ipSuccessor = self.myIp
        self.idSuccessor = self.id
        
        
        
        self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)
        self.socketClient.bind("tcp://*:"+self.portClient)
        self.socketSuccessor.connect("tcp://"+self.myIp+":"+self.portSuccessor)

        self.makeDirectory()
        #self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)
        print("mi ruta :",PATH)

    def __str__(self):
        a = "Node --> {} | Sucesor --> {}".format(self.id,self.idSuccessor)
        b = "SuccessorCon --> {}:{}".format(self.ipSuccessor,self.portSuccessor)
        return a +'\n'+b
    
    def getIp(self):
        nombre = sk.gethostname()
        direccion = sk.gethostbyname(nombre)
        return direccion

    def getId(self):
        return self.id

    def getMyClient(self):
        #retorna una cadena con direccion ip del nodo + puerto por donde atiende solicitudes de cliente
        return self.getIp()+":"+self.portClient

    def getMyPredecessor(self):
        #retorno mi ip+puerto predecesor para que alguien se conecte a mi como mi nuevo predecesor
        return self.myIp + ":" + self.portPredecessor

    def getMySuccessor(self):
        #retorno la ip+puerto de mu sucesor para que alguien se conecte a el como su nuevo sucesor
        return  self.ipSuccessor + ":" + self.portSuccessor

    def setSuccessor(self,S,id):
        #recibe una cadena con dir ip + puerto para asignar a este como mi sucesor
        self.socketSuccessor.disconnect("tcp://"+self.myIp+":"+self.portSuccessor)
        self.socketSuccessor.connect("tcp://"+S)
        self.ipSuccessor, self.portSuccessor = S.split(':')
        self.idSuccessor = id

    def calculateResponsibilities(self,idPredecessor):
        self.R[0] = idPredecessor + 1
        # Revisar si tengo archivos para que mi predecesor los almacene

    def validate(self,idNewPeer):
        #si mi sucesor es menor a mi significa que estoy en la frontera
        #aqui se debe hacer uso de la fingertable para siguiente salto, en caso de el nuevo nodo no sea sucesor de este
        if self.id == idNewPeer:
            #n repetido, no valido
            return -1
        elif self.id == self.idSuccessor:
            #segundo nodo, es indistintiva su ubicacion
            return True
        elif self.id > self.idSuccessor:
            #frontera -- punto de cambio del ultimo al primero
            if idNewPeer > self.id: 
                #ejm    NodoActual --> 54    SiguienteNodo --> 1     NuevoNodo--> 56
                return True
            else:
                if idNewPeer < self.idSuccessor:
                    #ejm    NodoActual --> 54    SiguienteNodo --> 1     NuevoNodo--> 0
                    return True
                else:
                    return False
        else:
            #normal, mi sucesor es mayor a mi   ... self.id < self.idSuccessor
            if idNewPeer > self.id:

                if idNewPeer < self.idSuccessor:
                    #ejm    NodoActual --> 5    SiguienteNodo --> 8     NuevoNodo--> 6
                    #si el nuevo nodo esta entre mi suceso y yo
                    return True
                else:
                    #ejm    NodoActual --> 5    SiguienteNodo --> 8     NuevoNodo--> 10
                    #el nuevo nodo no esta entre mi sucesor y yo
                    return False
            else:
                #aun no encuentro una posible ubicacion
                return False

    def join(self):
        print("intentando ingresar")
        #dir es la direcion a donde voy a solicitar mi ingreso por primera vez
        #   127.0.0.1
        dir = "192.168.0.4" + ":" + "5555"
        
        flag = False

        conexion = ctx.socket(zmq.REQ)
        while True:
            conexion.connect("tcp://"+ dir)
            conexion.send_json({"request":"join","id":self.id})
            m = conexion.recv_json()
            #print("respuesta ",m["reply"])
            if m["reply"] == True:
                self.setSuccessor(m["S"],m["id"])
                self.calculateResponsibilities(m["myId"])
                #debo completar el ingreso haciendo el join2
                conexion.send_json({"request":"join2","S":self.getMyPredecessor(),"id":self.id})
                _ = conexion.recv_json()
                print("El nodo ingreso!!!")
                self.socketSuccessor.send_json({"request":"updateR","id":self.id})
                _ = self.socketSuccessor.recv_json()
                
                #Hablar con mi sucesor para comprobar si me debe enviar archivos
                self.negotiateFiles()
                flag = True
                break
            elif m["reply"] == False:
                #me conecto al siguiente cliente
                conexion.disconnect("tcp://"+ dir)
                dir = m["nextIp"]
                
            elif m["reply"] == -1:
                print("Acceso a la red no permitido")
                flag = False
                break
        return flag
    
    def validateResponsibility(self,m):
        #valida si un archivo debe ser guardado por este nodo y de ser asi lo almacena
        id      = m["id"]
        name    = m["name"]
        content = m["content"]
        #esta validacion no aplica para el ultimo nodo de mayor id
        #ya que no tiene en cuenta un subconjunto de resposabilidad
        if self.R[0] < self.R[1]:

            if id > self.R[0] and id <= self.R[1]:
                return self.saveFile(name,content)
                
            else:
                return False
        else:
            #si es el nodo frontera
            if (id > self.R[0] and id >= self.R[1]) or (id < self.R[0] and id <= self.R[1]):
                return self.saveFile(name,content)
            else :
                return False

    def printPeer(self):
        cadena = "Soy el nodo : {}  con sucesor :{} \n y responsabilidades {}".format(self.id,self.idSuccessor,self.R)
        return cadena
    
    def makeDirectory(self):
        #crear un directorio con la ip + el id del peer donde se van a guardar la informacion
        global PATH
        directorio = os.getcwd()        
        carpeta = "/" + str(self.myIp) + ":" + str(self.id)
        ruta = directorio+carpeta
        try:    
            os.stat(ruta)
        except:
            os.mkdir(ruta)
        PATH = ruta
    
    def saveFile(self,name,content):
        #content = content.decode('utf-8')
        #Recibe un nombre y bytes para guardar un archivo en la carpeta con ruta PATH
        with open(PATH+'/'+ name, 'wb') as f:
            f.write(content)
            f.close()    
        return True

    def validateUpload(self,m):
        #id = (int(m["name"], 16) % (1024 * 1024))
        #esta validacion no aplica para el ultimo nodo de mayor id
        #ya que no tiene en cuenta un subconjunto de resposabilidad
        id = m["id"]
        if self.R[0] < self.R[1]:
            if id > self.R[0] and id <= self.R[1]:
                return  True
                #return self.saveFile(m["name"],m["content"])
            else:
                return False
        else:
            if (id > self.R[0] and id > self.R[1]) or (id < self.R[0] and id <= self.R[1]):
                return True
                #return self.saveFile(m["name"],m["content"])
            else:
                return False

    def validateDownload(self,m):
        #calcular el id del archivo
        id = (int(m["name"], 16) % (1024 * 1024))
        #esta validacion no aplica para el ultimo nodo de mayor id
        #ya que no tiene en cuenta un subconjunto de resposabilidad
        if self.R[0] < self.R[1]:
            if id > self.R[0] and id <= self.R[1]:
                return self.sendFile(m)
            else:
                return False
        else:
            if (id > self.R[0] and id > self.R[1]) or (id < self.R[0] and id <= self.R[1]):
                return self.sendFile(m)
            else:
                return False
                 
    def sendFile(self,m):
        #recibe el nombre de un achivo y lo retorna si lo contiene
        name = m["name"]
        fileList = os.listdir(PATH)
        content = None
        if name in fileList:
        
            with open(PATH + '/'+ name,'rb') as f:
                content = f.read()
                f.close()
            return content
        else:
            return False
    
    def checkFiles(self):
        # Reviso que archivo no me pertenece para enviarlo de regreso
        fileList = os.listdir(PATH)
        fileToSend = []
        if len(fileList) == 0:
            return False
        else:
            for file in fileList:
                fileNameToInt = int(file, 16)  % (1024*1024*1024) # nombre hash convertido a  numero (id del archivo)
                dic = {"id":fileNameToInt}
                if self.validateUpload(dic):
                    pass
                else:
                    fileToSend.append(file)
        #en fileToSend estan los nombres de los archivos que no pertenencen a este nodo si no a su predecesor
        if len(fileToSend) == 0:
            # Todos pertenencen
            return False
        else:
            #se los tengo que enviar
            self.socketPredecessor.send_json({"reply":True,"cant":len(fileToSend)})
    
            #procedo a enviar archivo por archivo
            for x in fileToSend:
                _ = self.socketPredecessor.recv_string()
                with open(PATH + '/' + x,'rb') as f:
                    content = f.read()
                    self.socketPredecessor.send_multipart([x.encode('utf-8'),content])
                    f.close()
                os.remove(PATH + '/'+ x) # Borro el archivo
            _ = self.socketPredecessor.recv_string()
            
        pass

    def negotiateFiles(self):
        # Hecha la conexion con el sucesor, le pregunto que tiene para mi
        self.socketSuccessor.send_json({"request":"WNO"})
        m = self.socketSuccessor.recv_json()
        if m["reply"] == False:
            return False
        else:
            iteration = m["cant"] # Cantidad de archivos a recibir
            self.socketSuccessor.send_string("ok")
            for i in range(iteration):
                F = self.socketSuccessor.recv_multipart()
                self.saveFile(F[0].decode('utf-8'),F[1])
                self.socketSuccessor.send_string("ok")
            return True




