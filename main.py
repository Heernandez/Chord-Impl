from Peer import Peer
import zmq
import socket as inf

first = True

ctx = zmq.Context()
MyPeer = Peer(4)
poll = zmq.Poller()
'''
puerto atender al cliente  5555
puerto atender al predesesor  4444
puerto hablar al sucesor 6666

'''
poll.register(MyPeer.socketClient, zmq.POLLIN)
poll.register(MyPeer.socketPredecessor, zmq.POLLIN)

if first:
    pass
else:
    print("other peer")
    MyPeer.join()

'''
por el socket cliente recibo solicitudes de unirse
por el socket predecesor recibo solicitudes de fijar predecesor nuevo, ip, id
'''

while True:
    sockets = dict(poll.poll(1))
    if MyPeer.socketClient in sockets:
        
        m = MyPeer.socketClient.recv_json()
        print("solicitud {}".format(m["mensaje"]))
        resp = {}
        if m["mensaje"] == "join":
            print("miremos a ver {}".format(m["id"]))
            #verificar si aqui es o sigue buscando lugar
            MyPeer.socketSuccessor.send_json({"mensaje":"id"})
            sckts = dict(poll.poll(1))
            if MyPeer.socketPredecessor in sckts:
                    
                ok = MyPeer.comprobar(m["id"],defecto = True)
                print("respuesta es ",ok)
                if ok:
                    #llego a donde debe estar
                    resp["siguiente"] = False
                    MyPeer.socketClient.send_json(resp)
                else:
                    #no llego todavia a su posicion
                    resp["siguiente"] = True
                    resp["ip"] = MyPeer.conexionSiguiente()
                    MyPeer.socketClient.send_json(resp)
            
        elif m["mensaje"] == "entrar":
            S = m["S"]
            resp["S"] = MyPeer.getDirSuccesor()
            MyPeer.setSuccessor(S)
            MyPeer.socketClient.send_json(resp)


    elif MyPeer.socketPredecessor in sockets:
        m = MyPeer.socketPredecessor.recv_json()
        print("solicitud {}".format(m["mensaje"]))
        resp = {}
        if m["mensaje"] == "id":
            resp["id"] = MyPeer.getId()
            MyPeer.socketPredecessor.send_json(resp)

        elif m["mensaje"] == "ip":
            resp["ip"] = MyPeer.getIp()
            MyPeer.socketPredecessor.send_json(resp)
        
        elif m["mensaje"]  == "entrar":
            nuevoS = m["S"]
            MyPeer.socketPredecessor.send_json()
            MyPeer.setSuccesor(nuevoS)
