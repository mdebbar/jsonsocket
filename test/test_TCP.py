from unittest import TestCase

from jsonsocket.tcp import ServerAsync, Client


def new_client(addr, _srv):
    print("New client: %s" % str(addr))


def new_data(data, _srv):
    print("New data : %s" % str(data))
    # Echo
    _srv.send(data)


def disconnect_client(addr, _srv):
    print("Client disconnected: %s" % str(addr))


class TestTCP(TestCase):
    def test_general(self):
        port = 1234
        srv = ServerAsync("localhost", port, new_client, new_data, disconnect_client, timeout=1)

        with srv:
            cl = Client()
            cl.connect("localhost", port)
            cl.send({"text": "Bonjour le monde!"})
            res = cl.recv()
            print("Received the following echo:")
            print(res)
            print("Disconnecting")
            cl.close()

    def test_numpy(self):
        import numpy as np
        port = 1237
        srv = ServerAsync("localhost", port, new_client, new_data, disconnect_client, timeout=1)

        payload = {"numpy": np.linspace(0, 1, 9)}
        with srv:
            cl = Client()
            cl.connect("localhost", port)
            cl.send(payload)
            res = cl.recv()
            print("Received the following echo:")
            print(res)
            print("Disconnecting")
            cl.close()

    def test_pandas(self):
        import numpy as np
        from pandas import DataFrame

        port = 1236
        srv = ServerAsync("localhost", port, new_client, new_data, disconnect_client, timeout=1)

        payload = DataFrame(dict(A=[1, 2, 3], B=[4, 5, 6]))
        with srv:
            cl = Client()
            cl.connect("localhost", port)
            cl.send(payload)
            res = cl.recv()
            print("Received the following echo:")
            print(res)
            print("Disconnecting")
            cl.close()
