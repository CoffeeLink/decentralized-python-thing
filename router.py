# Purpose: Router for data traffic
from trafic import *
import threading
import socket

class NodeHandler:
    connection : socket.socket
    node_id : str
    router_id : str
    
    is_waiting_for_init_response : bool = True
    
    recive_loop_thread : threading.Thread = None
    
    def __init__(self, connection : socket.socket, node_id : str, router_id : str = "r1") -> None:
        self.connection = connection
        self.node_id = node_id
        self.router_id = router_id
        
    def send_p(self, payload : Payload):
        self.connection.send(payload.ToJson().encode("utf-8"))
        
    def send(self, body : Body):
        self.send_p(Payload(self.router_id, self.node_id, body))
    
    def processPacket(self, packet : str) -> Payload | None:
        try:
            p = Payload.FromJson(packet)
        except Exception as e:
            print(f"Node {self.node_id}-{self.connection.getpeername()[0]} sent invalid data :(")
            print(f"Disconnecting node {self.node_id}-{self.connection.getpeername()[0]} :(")
            
            self.connection.close()
            return None
        return p
    
    def disconnect(self):
        self.send(Body("node_disconnect", -1))
        self.connection.close()
    
    def processData(self, payload : Payload):
        if payload.body.msg_type == "node_disconnect":
            print(f"Node {self.node_id} disconnected")
            self.connection.close()
            return
    
    def recive_loop(self):
        while True:
            data = self.connection.recv(1024).decode("utf-8")
            if not data:
                break
            p = self.processPacket(data)
            if p is None:
                break
            self.processData(p)
            self.on_node_event(p)
    
    def start(self):
        self.recive_loop_thread = threading.Thread(target=self.recive_loop)
        self.recive_loop_thread.start()
    
    #overide this to get node events
    def on_node_event(self, payload : Payload):
        pass
class DataTrafficRouter:
    ip : str
    port : int
    
    nodes : dict[str, NodeHandler] = {} #node_id -> thread
    latest_node_id : int = 0
    latest_node_message_id : int = 0
    
    listen_thread : threading.Thread = None
    sock : socket.socket = None
    
    
    def __init__(self, ip : str, port : int) -> None:
        self.ip = ip
        self.port = port
        
    def start(self):
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()
    
    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen()
        
        while True:
            conn, addr = self.sock.accept()
            print(f"New connection from {addr[0]}")
            self.on_new_connection(conn, addr)
    
    def on_new_connection(self, connection : socket.socket, addr : tuple):
        node_id = self.get_new_node_id()
        node = NodeHandler(connection, node_id)
        node.on_node_event = self.on_node_event
        self.nodes[node_id] = node
        node.start()
        
        nodeInit = Body("node_init", self.get_new_node_message_id())
        nodeInit.addField("node_id", node_id)
        nodeInit.addField("router_id", "r1")
        
        self.sendToNode(node_id, nodeInit)
    
    def get_new_node_id(self) -> str:
        self.latest_node_id += 1
        return f"n{self.latest_node_id}"
    
    def get_new_node_message_id(self) -> str:
        self.latest_node_message_id += 1
        return f"m{self.latest_node_message_id}"
    
    def on_node_event(self, payload : Payload):
        if payload.body.msg_type == "node_init_ok":
            if self.nodes[payload.src].is_waiting_for_init_response:
                self.nodes[payload.src].is_waiting_for_init_response = False
                print(f"Node {payload.src} is initialized")
                return
        if payload.body.msg_type == "node_init_fail":
            if self.nodes[payload.src].is_waiting_for_init_response:
                print(f"Node {payload.src} failed to initialize")
                self.nodes[payload.src].disconnect()
                return
    
    def sendToNode(self, node_id : str, body : Body):
        self.nodes[node_id].send(body)
    
    def handle_router_msg(self, payload : Payload):
        """when a node sends a payload to the router

        Args:
            payload (Payload): payload sent by node
        """
        
        pass
    
        
        