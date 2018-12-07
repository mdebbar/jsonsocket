#!/usr/bin/env python3
import socket
from threading import Thread

from jsonsocket.errors import NoClient, ConnectFirst
from jsonsocket.helpers import send as _send, receive as _recv, TimeoutError


class Server(object):
    """
    A JSON socket server used to communicate with a JSON socket client. All the
    data is serialized in JSON. How to use it:

    server = Server(host, port)
    while True:
      server.accept()
      data = server.recv()
      # shortcut: data = server.accept().recv()
      server.send({'status': 'ok'})
    """

    backlog = 5
    client = None

    def __init__(self, host, port):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(self.backlog)

    def __del__(self):
        self.close()

    @property
    def client_connected(self):
        return self.client is not None

    def accept(self):
        # if a client is already connected, disconnect it
        if self.client:
            self.client.close()
        self.client, self.client_addr = self.socket.accept()
        return self

    def send(self, data):
        if not self.client:
            raise NoClient()
        _send(self.client, data, socket_type="tcp")
        return self

    def recv(self, close_on_timeout=False, **kwargs):
        if not self.client:
            raise NoClient()
        try:
            res = _recv(self.client, socket_type="tcp", **kwargs)
        except TimeoutError:
            if close_on_timeout:
                self.close()
            return None
        return res

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.socket:
            self.socket.close()
            self.socket = None


class Client(object):
    """
    A JSON socket client used to communicate with a JSON socket server. All the
    data is serialized in JSON. How to use it:

    data = {
      'name': 'Patrick Jane',
      'age': 45,
      'children': ['Susie', 'Mike', 'Philip']
    }
    client = Client()
    client.connect(host, port)
    client.send(data)
    response = client.recv()
    # or in one line:
    response = Client().connect(host, port).send(data).recv()
    """

    socket = None

    def __del__(self):
        self.close()

    def connect(self, host, port):
        self.socket = socket.socket()
        self.socket.connect((host, port))
        return self

    def send(self, data):
        if not self.socket:
            raise ConnectFirst()
        _send(self.socket, data, socket_type="tcp")
        return self

    def recv(self, **kwargs):
        if not self.socket:
            raise ConnectFirst()
        return _recv(self.socket, socket_type="tcp", **kwargs)

    def recv_and_close(self, **kwargs):
        data = self.recv(**kwargs)
        self.close()
        return data

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


class ServerAsync(Thread):
    def __init__(self, host, port, new_client_callback, new_message_callback, client_disconnect_callback=None,
                 exception_callback=None, timeout=5):
        super(ServerAsync, self).__init__()
        self.exception_callback = exception_callback
        self.client_disconnect_callback = client_disconnect_callback
        self.timeout = timeout
        self.new_message_callback = new_message_callback
        self.new_client_callback = new_client_callback
        self.server = Server(host, port)
        self.__running = True

    def stop(self):
        self.__running = False

    def run(self):
        try:
            self.__running = True

            while self.__running:
                self.server.accept()
                client_addr = self.server.client_addr
                if self.new_client_callback:
                    self.new_client_callback(client_addr, self)
                while 1:
                    try:
                        data = self.server.recv(timeout=self.timeout)
                    except (NoClient, socket.error):
                        break
                    if data is not None:
                        self.new_message_callback(data, self)
                if self.client_disconnect_callback:
                    self.client_disconnect_callback(client_addr, self)
        except Exception as e:
            if self.exception_callback:
                self.exception_callback(e)
            else:
                raise

    def send(self, data):
        self.server.send(data)

    @property
    def client_addr(self):
        return self.server.client_addr

    @property
    def client(self):
        return self.server.client

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.server.close()
        self.join()
