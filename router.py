# Purpose: Router for data traffic
from trafic import *
import threading
import socket

class DataTrafficRouter:
    ip : str
    port : int
    
    nodes : dict[str, tuple[threading.Thread, socket.socket]] = {} #node_id -> thread
    latest_node_id : int = 0
    latest_node_message_id : int = 0
    
    listen_thread : threading.Thread = None
    sock : socket.socket = None
    
    def __init__(self, ip : str, port : int) -> None:
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        
    def start(self):
        self.sock.listen(5)
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()
        self.listen_thread.join()
    
    def listen(self):
        while True:
            conn, addr = self.sock.accept()
            self.handle_connection(conn)
    
    def routeData(self, payload : Payload):
        if payload.dest not in self.nodes:
            print(f"Node {payload.src} tried to send data to {payload.dest} but it does not exist")
            return
        
        sock = self.nodes[payload.dest][1]
        sock.send(payload.ToJson().encode("utf-8"))
        
    def handle_node(self, sock : socket.socket, node_id : str):
        initBody = Body("node_init", self.latest_node_message_id)
        initBody.addField("node_id", node_id)
        initPayload = Payload("router-1", node_id, initBody)
        sock.send(initPayload.ToJson().encode("utf-8"))
        recv = sock.recv(1024).decode("utf-8")
        p = Payload.FromJson(recv)
        if p.body.msg_type != "node_init_ok":
            raise Exception("Node did not respond with node_init_ok")
        else:
            print(f"Node {node_id} connected successfully")
        
        data = "y"
        while True:
            data = sock.recv(1024).decode("utf-8")
            if not data:
                break
            p = Payload.FromJson(data)
            if p.body.msg_type == "node_disconnect":
                print(f"Node {node_id} disconnected")
                sock.close()
                return
            self.routeData(p)
            
        
        print(f"Node {node_id} disconnected unexpectedly")
            
    
    def handle_connection(self, conn : socket.socket):
        node_name = f"node-{self.latest_node_id}"
        self.latest_node_id += 1
        
        th = threading.Thread(target=self.handle_node, args=(conn, node_name))
        th.start()
        self.nodes[node_name] = th
        