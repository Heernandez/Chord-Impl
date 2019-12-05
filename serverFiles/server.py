import zmq

context = zmq.Context()
server = context.socket(zmq.REP)
server.bind("tcp://*:5555")

tableSongs = {
    "pa las que sea" : "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "olvidala" : "5819b005d5c142ae151889bcbe0872bbbdbeecc26c4785a48e65b04abd7a6926"
}

while True:
    # wait for request from client
    nameSong = server.recv_string()
    hashSong = tableSongs[nameSong]
    print(hashSong)
    server.send_string(hashSong)
