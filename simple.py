import zmq
import time
from threading import Thread


class Server(Thread):
    def __init__(self, public_key, secret_key, port):
        super().__init__()
        self.ctx = zmq.Context()
        self.port = port
        self.public_key = public_key
        self.secret_key = secret_key

    def run(self):
        socket = self.ctx.socket(zmq.REP)
        socket.curve_server = True
        socket.curve_publickey = self.public_key
        socket.curve_secretkey = self.secret_key
        socket.bind("tcp://*:{}".format(self.port))

        while True:
            msg = socket.recv()
            print("Got {} on server".format(msg))
            socket.send(b'World')


class Client(Thread):
    def __init__(self, public_key, secret_key, server_key, port):
        super().__init__()
        self.ctx = zmq.Context()
        self.port = port
        self.public_key = public_key
        self.secret_key = secret_key
        self.server_key = server_key

    def run(self):
        socket = self.ctx.socket(zmq.REQ)
        socket.curve_publickey = self.public_key
        socket.curve_secretkey = self.secret_key
        socket.curve_serverkey = self.server_key
        socket.connect("tcp://127.0.0.1:{}".format(self.port))

        while True:
            socket.send(b'Hello ')
            msg = socket.recv()
            print("Got {} on client".format(msg))
            time.sleep(5)


def run():
    # generate keys for client and server
    server_public_key, server_secret_key = zmq.curve_keypair()
    client_public_key, client_secret_key = zmq.curve_keypair()

    # generate server and client
    port  = 5556
    server = Server(server_public_key, server_secret_key, port)
    client = Client(client_public_key, client_secret_key, server_public_key, port)
    server.start()
    client.start()


if __name__ == "__main__":
    run()