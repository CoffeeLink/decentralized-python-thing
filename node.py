import os
import threading
import enum
from typing import Callable
import logging

from sys import stdin, stdout

from trafic import *

class EventRegistry:
    event_listeners : dict = {} #event name -> list : func
    
    def __init__(self) -> None:
        self.event_listeners = {}
    
    def on_event(self, name : str):
        def event_inner(func):
            if name in self.event_listeners:
                self.event_listeners[name].append(func)
            else:
                self.event_listeners[name] = [func]
        return event_inner
    
    def event(self, type : str, payload : Payload):
        """Call this when an event occurs"""
        if type not in self.event_listeners:
            return
        
        for f in self.event_listeners[type]:
            f(payload)

class Node:
    name : str
    node_id : str
    
    tree : EventRegistry = EventRegistry()
    
    def __init__(self, name : str, node_id : str) -> None:
        self.name = name
        self.node_id = node_id
        
        self.tree = EventRegistry()
    
    #default event fucntions, not really doing anything but are here to be overwritten
    def on_recive(self, payload : Payload):
        pass
        
    def on_init(self, payload : Payload):
        pass
    
    def on_send(self, payload : Payload) -> Payload:
        """Use this to modify the payload before it is sent
        """
        return payload
    
    #tx/rx functions for sending and reciving data    
    def rx(self, recvied : str):
        try:
            payload = Payload.FromJson(recvied)
        except Exception as e:
            print("Error while parsing payload: " + str(e))
            return
        
        self.tree.event("on_recive", payload)
        self.tree.event(payload.body.msg_type, payload)
        
        if payload.body.msg_type == "node_init":
            self.on_init(payload)
    
    def tx(self, payload : Payload):
        stdout.write(payload.ToJson() + "\n")

    #the main loop function
    def listen(self):
        """Starts the main loop.
        """
        while True:
            line = stdin.readline()
            if line == "":
                break
            self.rx(line)

    
            