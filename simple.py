import zmq
import time
from threading import Thread


class Server(Thread):
    """
    Server thread just binds, prints messages that it receives, and sends "World" back.
    """

    def __init__(self, public_key, secret_key, port):
        super().__init__()
        self.ctx = zmq.Context()
        self.port = port
        self.public_key = public_key
        self.secret_key = secret_key

    def run(self):
        socket = self.ctx.socket(zmq.REP)

        # this is the curve/security logic
        socket.curve_server = True
        socket.curve_publickey = self.public_key
        socket.curve_secretkey = self.secret_key

        # standard binding
        socket.bind("tcp://*:{}".format(self.port))

        while True:
            msg = socket.recv()
            print("Got {} on server".format(msg))
            socket.send(b'World')


class Client(Thread):
    """
    Client thread just connects, sends "Hello", and prints whatever it gets back.
    """

    def __init__(self, public_key, secret_key, server_key, port):
        super().__init__()
        self.ctx = zmq.Context()
        self.port = port
        self.public_key = public_key
        self.secret_key = secret_key
        self.server_key = server_key

    def run(self):
        socket = self.ctx.socket(zmq.REQ)

        # this is the curve/security logic; the client socket needs the server public key so we can
        # encrypt the messages
        socket.curve_publickey = self.public_key
        socket.curve_secretkey = self.secret_key
        socket.curve_serverkey = self.server_key

        # standard connect
        socket.connect("tcp://127.0.0.1:{}".format(self.port))

        while True:
            socket.send(b'Hello ')
            msg = socket.recv()
            print("Got {} on client".format(msg))
            time.sleep(5)


def run():
    # NOTE: A few other things we could do is (1) whitelist client IP addresses (2) have a set of
    # authorized client keys to accept (3) use zmq.auth.load_certificate(..) and zmq.auth.create_certificates(..)

    # generate keys for client and server
    server_public_key, server_secret_key = zmq.curve_keypair()
    client_public_key, client_secret_key = zmq.curve_keypair()

    # generate server and client
    port = 5556
    server = Server(server_public_key, server_secret_key, port)
    client = Client(client_public_key, client_secret_key, server_public_key, port)
    server.start()
    client.start()


if __name__ == "__main__":
    run()