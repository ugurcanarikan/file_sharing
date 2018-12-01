from socket import *
from subprocess import check_output
import os

clear = 'clear'
if os.name == 'nt':
    clear = 'cls'
host = gethostbyname(gethostname())
host_name = "owl"
msg_port = 5001
discover_port = 5000
chatapp_port = 5124
buffer_size = 1024
msg_addr = (host, msg_port)
discover_addr = (host, discover_port)
chatapp_addr = (host, chatapp_port)
msg_server = socket(AF_INET, SOCK_STREAM)
discover_server = socket(AF_INET, SOCK_STREAM)
