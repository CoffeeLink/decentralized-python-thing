from trafic import *
from node import Node
from router import DataTrafficRouter

r = DataTrafficRouter("127.0.0.1", 5565)
r.start()

{"dest": "router", "src": "node-1", "body": {"msg_type": "node_init_ok", "msg_id": 1}}
{"dest": "router", "src": "node-1", "body": {"msg_type": "node_disconnect", "msg_id": 5}}