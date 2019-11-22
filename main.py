from Peer import Peer
import zmq

firstPeer = True
#firstPeer = False

ctx = zmq.Context()
MyPeer = Peer(1)
poll = zmq.Poller()

'''
    puerto atender al cliente  5555
    puerto atender al predecesor  4444
'''
#registrar sockets por los cuales se va a recibir mensajess
poll.register(MyPeer.socketClient, zmq.POLLIN)
poll.register(MyPeer.socketPredecessor, zmq.POLLIN)

login = False
if firstPeer:
    print("Iniciando Chord.....")
    login = True
else:
    print("Se va a unir el Peer con id {}".format(MyPeer.getId()))
    login = MyPeer.join()
    print(MyPeer.__str__())

while login:
    sockets = dict(poll.poll(1))
    if MyPeer.socketClient in sockets:
        m = MyPeer.socketClient.recv_json()
        print("Peticion {}  de nodo :{}".format(m["request"],m["id"]))
        if m["request"] == "join":
            #aqui recibo solicitud de unirse, si el que se une debe ir despues de mi
            #le valido y le envio mi sucesor
            idNewPeer = m["id"]
            validation = MyPeer.validate(idNewPeer)

            if validation == True:
                #va despues de mi, le envio direccion de mi sucesor para que sea su sucesor
                MyPeer.socketClient.send_json({"reply":True,"S":MyPeer.getMySuccessor(),"id":MyPeer.idSuccessor})
                #el cliente luego debe mandar un join2
            
            elif validation == False:
                #no va en esta posicion, debe avanzar al siguiente nodo para intentar ingresar
                MyPeer.socketSuccessor.send_json({"request":"client"})
                dirC = MyPeer.socketSuccessor.recv_json()
                dirC = dirC["client"]
                MyPeer.socketClient.send_json({"reply":False,"nextIp":dirC})
                
            elif validation == -1:
                #nodo no valido, se deniega ingreso
                MyPeer.socketClient.send_json({"reply":-1})
            
        elif m["request"] == "join2":
            #se unio un peer despues de mi, ahora el me envia su puerto predecesor
            #para que lo asocie como mi nuevo sucesor y ademas envia su id
            MyPeer.setSuccessor(m["S"],m["id"])
            MyPeer.socketClient.send_json({"reply":"ok"})

        elif m["request"] == "download":
            #recibo solicitud de descarga de un archivo
            pass
        
        elif m["request"] == "print":
            cadena = MyPeer.printPeer()
            print(MyPeer.__str__())
            MyPeer.socketSuccessor.send_json({"request":"client"})
            dirC = MyPeer.socketSuccessor.recv_json()
            dirC = dirC["client"]
            print("ahi tenes")
            MyPeer.socketClient.send_json({"string":cadena,"next":dirC})

    elif MyPeer.socketPredecessor in sockets:
        m = MyPeer.socketPredecessor.recv_json()
        
        if m["request"] == "ip":
            MyPeer.socketPredecessor.send_json({"ip":MyPeer.myIp})
        
        elif m["request"] == "predecessor":
            #recibo solicitud de cual es mi ip+puerto por donde atiendo a predecesores
            MyPeer.socketPredecessor.send_json({"P":MyPeer.getMyPredecessor()})
        
        elif m["request"] == "successor":
            #recibo solicitud de cual es ip+puerto al que me conecto a mi actual sucesor
            MyPeer.socketPredecessor.send_json({"S":MyPeer.getMySuccessor()})
        
        elif m["request"] == "client":
            #recibo solicitud de cual es mi ip+puerto por la cual atiendo clientes
            MyPeer.socketPredecessor.send_json({"client":MyPeer.getMyClient()})
        
        elif m["request"] == "updateFT":
            #recibe el id de su predecesor para recalcular las responsabilidades
            #y en caso tal enviar los archivos que deban cambiar de dueño
            pass
        
        #end behavioral