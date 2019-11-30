'''
Author : Luis H

En este script recorremos el anillo
e imprimimos el numero del nodo y su sucesor
'''

import zmq
ctx = zmq.Context()

conexion = ctx.socket(zmq.REQ)

def printChord(conexion):
    #se conecta una ip en espcifico
    dir = "192.168.0.4" + ":" + "5555"
    for i in range(4):
        conexion.connect("tcp://"+ dir)
        conexion.send_json({"request":"print","id":101010})
        m = conexion.recv_json()
        print("-------------------")
        print(m["reply"])
        conexion.connect("tcp://"+ dir)
        conexion.send_json({"request":"next","id":101010})
        m = conexion.recv_json()
        
        conexion.disconnect("tcp://"+ dir)
        dir = m["reply"]
        


printChord(conexion)