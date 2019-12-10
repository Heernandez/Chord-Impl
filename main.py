from Peer import Peer
import zmq

firstPeer = True
firstPeer = False

ctx = zmq.Context()
MyPeer = Peer()
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
    MyPeer.sendUpdate()
    print(MyPeer.__str__())

while login:
    #print("Esperando Solicitudes")
    sockets = dict(poll.poll(1))
    if MyPeer.socketClient in sockets:
        m = MyPeer.socketClient.recv_pyobj()
        print("Peticion {}  de nodo :{}".format(m["request"],m["id"]))
        
        if m["request"] == "join":
            #aqui recibo solicitud de unirse, si el que se une debe ir despues de mi
            #le valido y le envio mi sucesor
            idNewPeer = m["id"]
            validation = MyPeer.validate(idNewPeer)

            if validation == True:
                #va despues de mi, le envio direccion de mi sucesor para que sea su sucesor
                MyPeer.socketClient.send_pyobj({"reply":True,"S":MyPeer.getMySuccessor(),"id":MyPeer.idSuccessor,"myId":MyPeer.getId()})
                #el cliente luego debe mandar un join2
            
            elif validation == False:
                #no va en esta posicion, debe avanzar al siguiente nodo para intentar ingresar
                a = MyPeer.nextDecition(idNewPeer)
                if a == False:
                    MyPeer.socketSuccessor.send_pyobj({"request":"client"})
                    dirC = MyPeer.socketSuccessor.recv_pyobj()
                    dirC = dirC["client"]
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":dirC})
                else:
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":a})
                
            elif validation == -1:
                #nodo no valido, se deniega ingreso
                MyPeer.socketClient.send_pyobj({"reply":-1})
            
        elif m["request"] == "join2":
            #se unio un peer despues de mi, ahora el me envia su puerto predecesor
            #para que lo asocie como mi nuevo sucesor y ademas envia su id
            MyPeer.setSuccessor(m["S"],m["id"])
            MyPeer.socketClient.send_pyobj({"reply":"ok"})
            print(MyPeer.__str__())
            print("\n\n")
        
        elif m["request"] == "download":
            #recibo solicitud de descarga de un archivo
            #recibo un mensaje con id archivo y nombre(Hash),porque compruebo 
            #con id si esta en mi pertenencia
            validateDownload = MyPeer.validateDownload(m)
            
            if isinstance(validateDownload,bool):
                #no esta en esta posicion, debe avanzar al siguiente nodo para intentar descargar
                a = MyPeer.nextDecition((int(m["name"], 16) % (1024 * 1024 * 1024)))
                if a == False:
                    MyPeer.socketSuccessor.send_pyobj({"request":"client"})
                    dirC = MyPeer.socketSuccessor.recv_pyobj()
                    dirC = dirC["client"]
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":dirC})
                else:
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":a})
            else:
                MyPeer.socketClient.send_pyobj({"reply":True,"file":validateDownload})

        elif m["request"] == "upload":
            #print("solicitud para guardar {}".format(m["id"]))
            validationUpload = MyPeer.validateUpload(m)
            if validationUpload == False:
                a = MyPeer.nextDecition(m["id"])
                if a == False:
                        
                    #no va en esta posicion, debe avanzar al siguiente nodo para intentar guardar
                    MyPeer.socketSuccessor.send_pyobj({"request":"client"})
                    dirC = MyPeer.socketSuccessor.recv_pyobj()
                    dirC = dirC["client"]
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":dirC})
                else:
                    MyPeer.socketClient.send_pyobj({"reply":False,"nextIp":a})

            else:
                print("entro aqui")
                MyPeer.socketClient.send_pyobj({"reply":True})
                _ = MyPeer.saveFile(m["name"],m["bytes"])
            
        elif m["request"] == "print":
            cadena = MyPeer.printPeer()
            MyPeer.__str__()
            MyPeer.socketClient.send_pyobj({"reply":cadena})

        elif m["request"] == "next":
            MyPeer.socketSuccessor.send_pyobj({"request":"client"})
            dirC = MyPeer.socketSuccessor.recv_pyobj()
            dirC = dirC["client"]
            MyPeer.socketClient.send_pyobj({"reply":dirC})

        elif m["request"] == "updateFT":
            MyPeer.nextFillFingerTable(m["id"],m["range"],m["socket"])
            
            if MyPeer.idSuccessor == m["id"]:
                # Si el siguiente nodo es el que generó la actualizacion, no consulto el socket cliente
                MyPeer.socketClient.send_pyobj({"nextId":MyPeer.idSuccessor,
                                                "myId" : MyPeer.id,
                                                "myRange" : MyPeer.R,
                                                "mySocket" : MyPeer.getMyClient()
                
                })
            else:
                # Solicito el siguiente 
                MyPeer.socketSuccessor.send_pyobj({"request":"client"})
                dirC = MyPeer.socketSuccessor.recv_pyobj()
                dirC = dirC["client"]
                MyPeer.socketClient.send_pyobj({"nextId":MyPeer.idSuccessor,
                                                "nextIp":dirC,
                                                "myId" : MyPeer.id,
                                                "myRange" : MyPeer.R,
                                                "mySocket" : MyPeer.getMyClient()
                })   

    elif MyPeer.socketPredecessor in sockets:
        m = MyPeer.socketPredecessor.recv_pyobj()
       
        if m["request"] == "ip":
            MyPeer.socketPredecessor.send_pyobj({"ip":MyPeer.myIp})
        
        elif m["request"] == "predecessor":
            #recibo solicitud de cual es mi ip+puerto por donde atiendo a predecesores
            MyPeer.socketPredecessor.send_pyobj({"P":MyPeer.getMyPredecessor()})
        
        elif m["request"] == "successor":
            #recibo solicitud de cual es ip+puerto al que me conecto a mi actual sucesor
            MyPeer.socketPredecessor.send_pyobj({"S":MyPeer.getMySuccessor()})
        
        elif m["request"] == "client":
            #recibo solicitud de cual es mi ip+puerto por la cual atiendo clientes
            MyPeer.socketPredecessor.send_pyobj({"client":MyPeer.getMyClient()})
        
        elif m["request"] == "updateR":
            #recibe el id de su predecesor para recalcular las responsabilidades
            #y en caso tal enviar los archivos que deban cambiar de dueño
            MyPeer.calculateResponsibilities(m["id"])
            MyPeer.socketPredecessor.send_pyobj({"reply":"ok"})
        
        elif m["request"] == "WNO":
            print("Hora de Chequeo")
            #mi predecesor me pregunta ... What's New Oldman ...
            # reviso si tengo archivos de su pertenencia
            
            MyPeer.socketPredecessor.send_pyobj({"reply":"ok"})
            a = MyPeer.checkFiles(m)
            print("Fin Chequeo")
            
                
                
        #end behavioral