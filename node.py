import os
import threading
import enum
from typing import Callable
import logging

from sys import stdin, stdout

from trafic import *

class EventRegistry:
    event_listeners : dict = {} #event name -> list : func
    
    def __init__(self, eventDict : dict[str, list] = {}) -> None:
        self.event_listeners = eventDict
    
    def on_event(self, name : str):
        """Decorator for adding a function to an event

        Args:
            name (str): The name of the event
        """
        def event_inner(func):
            """ The actual decorator function :D """
            self.add_listener(name, func)
            
        return event_inner
    
    def add_listener(self, name : str, func : Callable[[Payload], None]):
        """Add a listener to an event

        Args:
            name (str): The name of the event
            func (Callable[[Payload], None]): The function to call when the event is triggered
        """
        if name in self.event_listeners:
            self.event_listeners[name].append(func)
        else:
            self.event_listeners[name] = [func]
    
    def event(self, type : str, payload : Payload):
        """Call this when an event occurs"""
        if type not in self.event_listeners:
            return
        
        for f in self.event_listeners[type]:
            f(payload)

class Node:
    name : str
    node_id : str
    
    default_event_list : dict[str, list] = {
        "on_recive": [],
        "on_send": [],
        "node_init": [],
    }
    
    eventTree : EventRegistry = EventRegistry()
    
    def __init__(self, name : str, node_id : str) -> None:
        self.name = name
        self.node_id = node_id
        self.eventTree = EventRegistry(self.default_event_list)
    
    #default event fucntions, not really doing anything but are here to be overwritten
    def on_recive(self, payload : Payload):
        pass
        
    def on_init(self, payload : Payload):
        self.node_id = payload.body.getField("node_id")
        init_ok = Body("node_init_ok", payload.body.msg_id + 1, payload.body.msg_id)
        self.send(init_ok, payload.src)
    
    def on_send(self, payload : Payload) -> Payload:
        """Use this to modify the payload before it is sent
        """
        return payload
    
    def send(self, body : Body, dest : str = "r1"):
        """Send a payload to the router

        Args:
            body (Body): The body to send
        """
        
        payload_to_send = Payload(self.node_id, dest, body)
        payload_to_send = self.on_send(payload_to_send)
        self.tx(payload_to_send)
    
    #tx/rx functions for sending and reciving data    
    def rx(self, recvied : str):
        try:
            payload = Payload.FromJson(recvied)
        except Exception as e:
            print("Error while parsing payload: " + str(e))
            return
        
        self.eventTree.event("on_recive", payload)
        self.eventTree.event(payload.body.msg_type, payload)
        
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

    
{"dest": "node-1", "src": "r-1", "body": {"msg_type": "node_init", "msg_id" : 1, "node_id": "node-1"}}