#!/usr/bin/env python3

from jsonsocket.jsonsocket import Client

host = 'localhost'
port = 8001

# Client code:
client = Client()
client.connect(host, port).send({'some_list': [123, 456]})
response = client.recv()
# response now is {'data': {'some_list': [123, 456]}}
client.close()




