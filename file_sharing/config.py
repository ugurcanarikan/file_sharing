from socket import *
import os
import subprocess

clear = 'clear'
if os.name == 'nt':
    clear = 'cls'
host = str(subprocess.check_output("ipconfig getifaddr en0", shell=True))[2:-3]
host_name = "bg"
msg_port = 5001
discover_port = 5000
chatapp_port = 5124
buffer_size = 1024
msg_addr = (host, msg_port)
discover_addr = (host, discover_port)
chatapp_addr = (host, chatapp_port)
msg_server = socket(AF_INET, SOCK_STREAM)
discover_server = socket(AF_INET, SOCK_STREAM)
