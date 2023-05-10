import socket
from trafic import *

class NodeLink:
    def recv(self) -> Payload:
        raise NotImplementedError
    
    def send(self, payload : Payload):
        raise NotImplementedError

class NodeNetLink(NodeLink):
    host : str
    host_port : int
    
    sock : socket.socket = None
    
    def __init__(self, host : str, host_port : int) -> None:
        self.host = host
        self.host_port = host_port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.host_port))
    
    def recv(self) -> Payload:
        data = self.sock.recv(1024)
        return Payload.FromJson(data.decode("utf-8"))
    
    def send(self, payload : Payload):
        self.sock.sendall(payload.ToJson().encode("utf-8"))

    def close(self):
        self.sock.close()
    
    def __del__(self):
        self.close()
    
    #debug stuff remove later TODO
    def __str__(self) -> str:
        return f"NodeNetLink({self.host}, {self.host_port})"