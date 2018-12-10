import socket

from jsonsocket.constants import broadcast_address
from jsonsocket.helpers import send as _send, receive as _recv

from jsonsocket.udp_async import Receiver, Advertiser


class UDP(object):
    def __init__(self):
        self.__threads = [None, None]  # receive and advertise

    def receive(self, host, port, timeout=None, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if host == broadcast_address:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except socket.error:
            raise Exception("Address %s:%i already in use" % (host,port))
        data, addr = _recv(s, timeout=timeout,socket_type="udp", **kwargs)
        return data, addr

    def send(self, data, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if ip == broadcast_address:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        _send(s, data, "udp", ip, port)

    @property
    def receiving(self):
        return self.__threads[1] is not None

    def receive_async(self, host, port, callback, timeout=5):
        if self.receiving:
            raise Exception("Already receiving")
        self.__threads[1] = t = Receiver(host, port, callback, timeout, self)
        t.start()
        return t

    def stop_receive_async(self):
        if not self.receiving:
            raise Exception("Not receiving")
        t = self.__threads[1]
        t.stop()
        self.__threads[1] = None

    @property
    def advertising(self):
        return self.__threads[0] is not None

    def advertise(self, data, period, ip, port):
        if self.advertising:
            raise ValueError("Already advertising!")
        self.__threads[0] = t = Advertiser(ip, port, data, period, self)
        t.start()
        return t

    def stop_advertising(self):
        if not self.advertising:
            raise Exception("Not advertising")
        t = self.__threads[0]
        t.stop()
        t.join()
        self.__threads[0] = None

    def join(self):
        for t in self.__threads:
            if t is not None:
                t.join()
