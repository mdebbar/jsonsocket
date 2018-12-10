class IncorrectLength(Exception):
    def __init__(self,message,length):
        super(IncorrectLength, self).__init__("Incorrect transmitted length")
        self.content = message
        self.length = length


class NoClient(Exception):
    def __init__(self):
        super(NoClient, self).__init__('Cannot send data, no client is connected')


class ConnectFirst(Exception):
    def __init__(self):
        super(ConnectFirst, self).__init__('You have to connect first before sending data')


class AddressAlreadyInUse(Exception):
    def __init__(self, host, port):
        super(AddressAlreadyInUse, self).__init__("Address %s:%i already in use" % (host, port))
        self.host = host
        self.port = port