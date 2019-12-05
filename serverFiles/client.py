import zmq

context = zmq.Context()
client = context.socket(zmq.REQ)
client.connect("tcp://localhost:5555")


nameSong = "olvidala"

client.send_string(nameSong)

hashSong = client.recv_string()
print(hashSong)

