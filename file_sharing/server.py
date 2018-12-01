from socket import *
from threading import Thread
from subprocess import check_output, call
from config import *
from sys import stdin
import os
from hashlib import md5

def get_input():
    return stdin.readline().rstrip(" \n\r")
def send_discovery():
    arr = host.split(".")
    arr.pop()
    ip = ".".join(arr)
    threads = []
    for i in range(1, 255):
        recvip = ip + "." + str(i)
        discover_pck = "0;" + host + ";" + host_name + ";" + recvip + ";"
        thread = Thread(target=send_pck, args=((recvip, discover_port), discover_pck))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
#    print("disovery finished")
def send_pck(to, pck):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(20)
    try:
        sock.connect(to)
        sock.send(bytes(pck, "utf8"))
    except ConnectionRefusedError:
        pass
        #print("connection refused")
    except timeout:
        pass
        #print("connection timeout")
    except OSError:
        pass
#        print(to)
    sock.close()
def accept_discovery():
    while True:
#        print("hello?")
        try:
            client, client_address = discover_server.accept()
#            print("someone is here "+ client_address[0])
            discover_pck = client.recv(buffer_size).decode("utf8")
            try:
                mod, senderip, sendername, recvip, recvname = discover_pck.split(";")
            except ValueError:
                pass
#                print("im sad")
#            print(sendername)
            users.append(sendername)
            addresses[sendername] = senderip
            message_list[sendername] = []
            if mod == "0":
                discover_pck = "1;" + host + ";" + host_name + ";" + senderip + ";" + sendername
                client.send(bytes(discover_pck, "utf8"))
            client.close()
        except Exception as e:
            pass
#            print(e)
def accept_message():
    while True:
        client, client_address = msg_server.accept()
        client_ip = client_address[0]
        if not client_ip in addresses.values():
            break
        else:
            Thread(target=handle_client, args=(client, client_ip)).start()
def send_message(name, msg):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((addresses[name], 5001))
    pck = ""
    if name in message_encode:
        pck = host + ";" + md5(message_encode[name].encode("utf-8")).hexdigest() + ";" + msg
        message_encode[name] = md5(message_encode[name].encode("utf-8")).hexdigest()
    else:
        pck = host + ";" + md5("".encode("utf-8")).hexdigest() + ";" + msg
        message_encode[name] = md5("".encode("utf-8")).hexdigest()
    sock.send(bytes(pck,"utf8"))
    message_list[name].append("<You>: " + msg)
    sock.close()

def handle_client(client, client_ip):
    name = {v: k for k, v in addresses.items()}[client_ip]
    while True:
        msg = client.recv(buffer_size).decode("utf8")
        if msg != "":
            msg = msg.split(";")
            if len(msg) != 3:
                client.close()
                break
            if name in message_encode:
                if md5(message_encode[name].encode("utf-8")).hexdigest() == msg[1]:
                    message_list[name].append("<"+name+">: " + msg[2])
                    message_encode[name] = msg[1]
                else:
                    print("Someone is pretending to be "+name + "!")
                    client.close()
                    break
            else:
                message_list[name].append("<"+name+">: " + msg[2])
                message_encode[name] = msg[1]
        else:
            client.close()
            break

#def handle_client(client, client_ip):
#    name = {v: k for k, v in addresses.items()}[client_ip]
#    print("connection established with " + name)
#    while True:
#        msg = client.recv(buffer_size)
#        if msg != bytes("{q}", "utf8"):
#            pass
#            write_to_chatapp(msg, name+": ")
#        else:
#            client.send(bytes("{q}", "utf8"))
#            client.close()
#            write_to_chatapp(bytes("%s has left the chat." % name, "utf8"))
#            break

users = []
clients = {}
addresses = {}
message_list = {}
message_encode = {}

#chatapp = socket(AF_INET, SOCK_STREAM)
#while True:
#    try:
#        chatapp.connect(chatapp_addr)
#        break
#    except ConnectionRefusedError:
#        t = call('clear', shell=True)
#        print("Waiting for ChatApp start...")
#        continue

msg_server.bind(msg_addr)
discover_server.bind(discover_addr)
msg_server.listen(30)
discover_server.listen(30)
print("Waiting for connection...")

# Start all the threads!
threads = []
threads.append(Thread(target=send_discovery))
threads.append(Thread(target=accept_discovery))
threads.append(Thread(target=accept_message))
for t in threads:
    t.start()

while True:
    t = call(clear, shell=True)
    print("1. Online users")
    print("2. Message rooms")
    print("3. Discovery")
    print("4. Exit")
    input = get_input()
    if input == "1":
        print("# Users")
        for u in message_list:
            print("#   " + u)
        stdin.readline()
    elif input == "2":
        print("With whom?")
        for u in message_list:
            print("#   " + u)
        input = get_input()
        if input in users:
            while True:
                t = call(clear, shell=True)
                print("### Room - %s" % input +" ###")
                for msg in message_list[input]:
                    print(msg)
                print("----------------")
                msg = get_input()
                if msg != "{q}":
                    #message_list[input].append("<You>: " + msg)
                    send_message(input, msg)
                else:
                    break
        else:
            print("user is not online")
            stdin.readline()
    elif input == "3":
        Thread(target=send_discovery).start()
    elif input == "4":
        os._exit(0)
    else:
        continue

# Ending the process
for t in threads:
    t.join()
msg_server.close()
discover_server.close()
