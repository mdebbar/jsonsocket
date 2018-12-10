from time import sleep
from unittest import TestCase

from jsonsocket.udp import UDP


def new_message(data, addr, _srv):
    new_message.n_received += 1
    print("SERVER: Received data:")
    print(data)
    # Echo
    _srv.send(data,*addr)
    if new_message.n_received>=4 and _srv.receiving:
        _srv.stop_receive_async()

new_message.n_received=0


class TestUDP(TestCase):
    def test_general(self):
        port = 1234
        data = {"data": "Bonjour!"}
        s = UDP()
        c = UDP()

        s.receive_async("0.0.0.0",port,new_message)
        sleep(1)
        c.send(data, "127.0.0.1", port)

        s.stop_receive_async()
        s.join()

    def test_advertize(self):
        port = 1234
        data = {"data": "Bonjour!"}
        s = UDP()
        c = UDP()

        s.receive_async("0.0.0.0", port, new_message)
        sleep(1)
        c.advertise(data, 1, "127.0.0.1", port)

        s.join()
        c.stop_advertising()
