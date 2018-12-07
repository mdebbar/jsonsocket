import socket
from threading import Thread
from time import sleep

import schedule

from jsonsocket.helpers import TimeoutError


class UDPThread(Thread):
    def __init__(self, host, port, client):
        super(UDPThread, self).__init__()
        self.client = client
        self.host = host
        self.port = port
        self.__stop = False

    @property
    def stopped(self):
        return self.__stop

    def stop(self):
        self.__stop = True

    def __del__(self):
        self.stop()
        self.join()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()


class Receiver(UDPThread):
    def __init__(self, host, port, callback, timeout, client):
        super(Receiver, self).__init__(host, port, client)
        self.timeout = timeout
        self.callback = callback

    def receive(self):
        res = self.client.receive(self.host, self.port, timeout=self.timeout)
        return res

    def run(self):
        while not self.stopped:
            res = None
            try:
                res = self.receive()
            except TimeoutError:
                pass
            if res is not None:
                self.callback(res[0], res[1], self.client)


class Advertiser(UDPThread):
    def __init__(self, host, port, data, interval, client):
        super(Advertiser, self).__init__(host, port, client)
        self.interval = interval
        self.data = data

    def send(self):
        self.client.send(self.data, self.host, self.port)

    def run(self):
        schedule.every(self.interval).seconds.do(self.send)
        while not self.stopped:
            schedule.run_pending()
            sleep(schedule.idle_seconds())
