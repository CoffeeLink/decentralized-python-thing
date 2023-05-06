import socket
import threading
import json
import os
import threading
import enum


class Body:
    msg_type : str #Must have
    msg_id : int = None
    in_return_to : int = None
    
    def __init__(self, msg_type : str, msg_id : int = None, in_return_to : int = None) -> None:
        self.msg_type = msg_type
        self.msg_id = msg_id
        self.in_return_to = in_return_to
    
    def toDict(self) -> dict:
        outDict = {"type": self.msg_type}
        if self.msg_id != None:
            outDict["msg_id"] = self.msg_id
        if self.in_return_to != None:
            outDict["in_reply_to"] = self.in_return_to
        return outDict
    
class EchoBody(Body):
    pass
    
class Payload:
    src : str = None
    dest : str = None
    body : Body = None
    
    def __init__(self, src : str, dest : str, body : Body) -> None:
        self.src = src
        self.dest = dest
        self.body = body
    
    def ToJson(self) -> str:
        dictOut = {"src": self.src, "dest": self.dest, "body": self.body.toDict()}
        return json.dumps(dictOut)

class Node:
    node_id : str = None
    node_ip : str = None
    
    def __init__(self) -> None:
        pass


b1 = Body("Echo", 2, 1)
p1 = Payload("n1", "c1", b1)
print(p1.ToJson())