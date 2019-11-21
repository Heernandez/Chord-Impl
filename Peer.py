import zmq
import socket as sk
ctx = zmq.Context()


class Peer:

    def __init__(self,id):
        # Id of the peer
        self.id = id

        self.myIp = self.getIp()
        # Sockets for comunication with the corresponding peers
        self.socketClient = ctx.socket(zmq.REP)
        #self.socketClient.bind("tcp://*:5555")
        self.socketPredecessor = ctx.socket(zmq.REP)
        self.socketSuccessor = ctx.socket(zmq.REQ)
        
        self.portClient = "5555"
        self.portPredecessor = "4444"
        self.portSuccesor = "4444"

        self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)
        self.socketClient.bind("tcp://*:"+self.portClient)
        self.socketSuccessor.connect("tcp://localhost:"+self.portSuccesor)
        #self.socketPredecessor.bind("tcp://*:"+self.portPredecessor)
        
    def getIp(self):
        nombre = sk.gethostname()
        direccion = sk.gethostbyname(nombre)
        return direccion

    def getId(self):
        return self.id

    def getDirClient(self):
        #retorna los parametros para una conexion al socket cliente
        return self.getIp()+":"+self.portClient

    def getDirSuccesor(self):
        #retorna los parametros de conexion al actual sucesor  
        return self.conexionSiguiente()+":"+self.portSuccessor
    
    def setSuccessor(self,S):
        #fija un nuevo sucesor para el nodo
        self.socketSuccessor.connect("tcp://"+S)
        self.portSuccessor = S.split(':')[1]


    def comprobar(self,id,defecto = False):
        
        if self.id < id:
            if defecto :
                return True
            self.socketSuccessor.send_json({"mensaje":"id"})
            m = self.socketSuccessor.recv_json()
            nextId = m["id"]
            
            if id > nextId and self.id != nextId:
                return False
            else:
                return True
        else:
            return False

    def join(self):
        ctx = zmq.Context()
        client = ctx.socket(zmq.REQ)
        #ip al peer inicial que se le hace la solicitud
        ip = "localhost"
        while True:
            #5555 es puerto de cliente
            client.connect("tcp://"+ip+":5555")
            d = {"mensaje" : "join", "id" : self.id}
            client.send_json(d)
            m = client.recv_json()
            
            if m["siguiente"] == False:

                resp = {"mensaje":"entrar",
                        "S":self.getIp()+":"+self.portPredecessor
                        }
                client.send_json(resp)
                m = client.recv_json()
                self.setSuccessor(m["S"])
                print("Nodo  agregado")

            else:
                ip = m["ip"]

    def conexionSiguiente(self):
        self.socketSuccessor.send_string("ip")
        m = self.socketSuccessor.recv_json()
        return m["ip"]
    
    def print(self):
        print("Mi Id es :",self.id)
        return self.conexionSiguiente()

