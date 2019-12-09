import zmq

'''
Este script ejecuta un servidor que contiene un diccionario que 
se asemeja a un magnet link 

Un Magnet Link, en contraposición a un .torrent es un archivo que identifica a 
los archivos a descargar no por su posición en un servidor, 
sino por el nombre único e inviolable que posee. 
Los enlaces magnéticos son sólo enlaces, que no tienen los archivos asociados con ellos,
 sólo datos para descargarlos


'''
context = zmq.Context()
server = context.socket(zmq.REP)
server.bind("tcp://*:5555")

tableSongs = {}

while True:
    # wait for request from client
    nameSong = server.recv_string()
    hashSong = tableSongs[nameSong]
    print(hashSong)
    server.send_string(hashSong)
