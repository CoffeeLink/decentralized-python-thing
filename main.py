import socket
import threading
import json
import os
import threading
import enum

class MsgField:
    name : str = None
    value : str = None
    
    def __init__(self, name : str, value : str | int | list) -> None:
        self.name = name
        self.value = value
    
    def addToDict(self, dictIn : dict) -> None:
        dictIn[self.name] = self.value
        return dictIn

class Body:
    msg_type : MsgField = None
    msg_id : MsgField = None
    msg_reply_to : MsgField = None
    
    fields : list[MsgField] = None
    
    @property
    def msg_type(self) -> str:
        return self.msg_type.value
    
    @msg_type.setter
    def msg_type(self, value : str) -> None:
        self.msg_type = MsgField("msg_type", value)
    
    @property
    def msg_id(self) -> int:
        return self.msg_id.value
    
    @msg_id.setter
    def msg_id(self, value : int) -> None:
        self.msg_id = MsgField("msg_id", value)
    
    @property
    def msg_reply_to(self) -> int:
        return self.msg_reply_to.value
    
    @msg_reply_to.setter
    def msg_reply_to(self, value : int) -> None:
        self.msg_reply_to = MsgField("msg_reply_to", value)
        
    def __init__(self, msg_type : str, msg_id : int, msg_reply_to : int) -> None:
        self.msg_type = MsgField("msg_type", msg_type)
        self.msg_id = MsgField("msg_id", msg_id)
        self.msg_reply_to = MsgField("msg_reply_to", msg_reply_to)
        self.fields = []
        
    def addField(self, name : str, value : str | int | list) -> None:
        self.fields.append(MsgField(name, value))
        
    def setField(self, name : str, value : str | int | list) -> None:
        for field in self.fields:
            if field.name == name:
                field.value = value
                return
        
        self.addField(name, value)
    
    def delField(self, name : str) -> None:
        for field in self.fields:
            if field.name == name:
                self.fields.remove(field)
                return
            
    def toDict(self) -> dict:
        dictOut = {}
        if self.msg_type != None:
            dictOut = self.msg_type.addToDict(dictOut)
        
        if self.msg_id != None:
            dictOut = self.msg_id.addToDict(dictOut)
        
        if self.msg_reply_to != None:
            dictOut = self.msg_reply_to.addToDict(dictOut)
        
        for field in self.fields:
            dictOut = field.addToDict(dictOut)
        
        return dictOut

    
class EchoBody(Body):
    
    echo : MsgField = None
    
    def __init__(self, msg_id : str, msg_reply_to : str, echo : str) -> None:
        super().__init__("Echo", msg_id, msg_reply_to)
    
    def toDict(self) -> dict:
        dictOut = super().toDict()
        return dictOut
    
    @property
    def echo(self) -> str:
        return self.echo.value
    
    @echo.setter
    def echo(self, value : str) -> None:
        self.echo = MsgField("echo", value)
    
    
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