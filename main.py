from trafic import *
from node import Node
from router import DataTrafficRouter

node = Node("node1", "n1")

t = node.eventTree

t.on_event("node_disconect")

node.listen()