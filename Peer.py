import zmq
import socket as sk
ctx = zmq.Context()

class Peer:

    def __init__(self,id):
        # Id del nodo
        self.id = id
        self.myIp = self.getIp()
        # Sockets del peer
        self.socketClient = ctx.socket(zmq.REP)
        self.socketPredecessor = ctx.socket(zmq.REP)
        self.socketSuccessor = ctx.socket(zmq.REQ)
        
        self.portClient =      "7777"  #5555    7777
        self.portPredecessor = "8888"  #4444    8888
        self.portSuccessor =   "8888"  #4444    8888

        self.ipSuccessor = self.myIp
        self.idSuccessor = id
        
        
        self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)
        self.socketClient.bind("tcp://*:"+self.portClient)
        self.socketSuccessor.connect("tcp://"+self.myIp+":"+self.portSuccessor)
        #self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)

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
        
        self.socketSuccessor.connect("tcp://"+S)
        self.ipSuccessor, self.portSuccessor = S.split(':')
        self.idSuccessor = id

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

        dir = "192.168.0.6" + ":" + "5555"
        
        flag = False

        conexion = ctx.socket(zmq.REQ)
        while True:
            conexion.connect("tcp://"+ dir)
            conexion.send_json({"request":"join","id":self.id})
            m = conexion.recv_json()
            #print("respuesta ",m["reply"])
            if m["reply"] == True:
                self.setSuccessor(m["S"],m["id"])
                #debo completar el ingreso haciendo el join2
                conexion.send_json({"request":"join2","S":self.getMyPredecessor(),"id":self.id})
                _ = conexion.recv_json()
                print("El nodo ingreso!!!")
                flag = True
                break
            elif m["reply"] == False:
                #me conecto al siguiente cliente
                dir = m["nextIp"]
                
            elif m["reply"] == -1:
                print("Acceso a la red no permitido")
                flag = False
        return flag
    
    def printPeer(self):
        cadena = "Soy el nodo : {}  con sucesor :{} ".format(self.id,self.idSuccessor)
        return cadena
