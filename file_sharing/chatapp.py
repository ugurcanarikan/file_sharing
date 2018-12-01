from socket import *
from threading import Thread
from subprocess import check_output, call
from config import *
from sys import stdin

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(chatapp_addr)
sock.listen(1)
print("Waiting for ChatServer start...")
server, server_addr = sock.accept()
print("App Started Successfuly")
# Get userlist
def get_userlist():
    server.setblocking(1)
    server.send(bytes("7;getuser", "utf8"))
    resp = server.recv(buffer_size).decode("utf8")
    users = resp.split(";")
    users.pop(0)
    print("getting users done")
    return users

while True:
    print("1. Online Users")
    print("2. Message Room /user/")
    input = stdin.readline().rstrip(" \n\r")
    users = get_userlist()
    if input == "1":
        print(",".join(users))
    elif input == "2":
        print("With whom?")
        input = stdin.readline().rstrip(" \n\r")
        if input in users:
            print("messaging with " + input)
        else:
            print("user not found")
    else:
        continue
