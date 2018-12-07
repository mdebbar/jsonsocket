from time import time

from jsonsocket.errors import IncorrectLength
from jsonsocket.serialize import serialize, deserialize
from socket import timeout as tmout


class TimeoutError(Exception):
    pass


def send(socket, data, socket_type="tcp", *args):
    serialized = serialize(data)
    # send the length of the serialized data first
    message = '{}\n'.format(len(serialized)).encode('utf-8')

    if socket_type == "tcp":
        socket.send(message)
        # send the serialized data
        socket.sendall(serialized)
    elif socket_type == "udp":
        content = message + serialized + "\n"
        socket.sendto(content, args)


def receive(socket, socket_type="tcp", timeout=None):
    # read the length of the data, letter by letter until we reach EOL
    length_str = ''
    tcp = socket_type == "tcp"
    t0 = time()
    if tcp:
        char = socket.recv(1)
        while char != b'\n' and (timeout is None or (timeout is not None and (time() - t0) < timeout)):
            length_str += char.decode('utf-8')
            char = socket.recv(1)
        if length_str == '':
            raise TimeoutError("Timeout listening for data")
        total = int(length_str)
        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = socket.recv_into(view[next_offset:], total - next_offset)
            next_offset += recv_size
        deserialized = deserialize(view.tobytes())
        return deserialized
    else:
        if timeout:
            socket.settimeout(timeout)
        try:
            char, addr = socket.recvfrom(2048 ** 2)
            length, char = char.split("\n")[:2]
            if len(char) != int(length):
                raise IncorrectLength(char,length)
            deserialized = deserialize(char)
            return deserialized, addr
        except tmout:
            raise TimeoutError("Timout listening for data")
