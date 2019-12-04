'''
Author : Luis H

En este script recorremos el anillo
e imprimimos el numero del nodo y su sucesor
'''

import zmq
from dibujarGrafo import *
ctx = zmq.Context()

conexion = ctx.socket(zmq.REQ)

Grafo = []


def printChord(conexion):
    global Grafo
    #se conecta una ip en espcifico
    dir = "127.0.0.1" + ":" + "5555"
    for i in range(4):
        conexion.connect("tcp://"+ dir)
        conexion.send_pyobj({"request":"print","id":101010})
        m = conexion.recv_pyobj()
        print("-------------------")
        print(m["reply"])
        Grafo.append(int(m["reply"]))
        conexion.connect("tcp://"+ dir)
        conexion.send_pyobj({"request":"next","id":101010})
        m = conexion.recv_pyobj()
        conexion.disconnect("tcp://"+ dir)
        dir = m["reply"]

printChord(conexion)
dibujarChord(Grafo)