from socket import *
from threading import Thread
from subprocess import check_output, call
from config import *
from sys import stdin
import os
from hashlib import md5
import subprocess

def get_file_from_seeders():
    global file_to_download_size
    print("file name and size: ", file_to_download," ",file_to_download_size)
    print("for now we are giving 846 as size")
    file_to_download_size = 846
    file_packet_size = file_to_download_size / packet_size
    received_file = []
    #select seeder, send it a message contatining "6; host_ip, listening port,filename,chunk_no"
    seeder = seeders.pop() #seeder = clientip
    msg = "6;"+ host + ";" + str(3500) +";" + file_to_download + ";" + "1" #listening from port 3500
    send_pck((seeder,discover_port),msg)
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(("", 3500))
    data, addr = s.recvfrom(4096)
    #if it accepts it returns 6;ACK
    received_msg = data.decode().split(";")
    rwnd = 1
    if(received_msg[0] == 7 and received_msg[1]=="Start"): #it starts to send
        msg = "8;"+ str(rwnd)
        send_pck((seeder, discover_port), msg)

    index = 0
    s.setblocking(True)
    while (True):
        try:
            #receive data
            data = s.recv(4096)
            packet_num = data.decode().split(";")[0] #sends packet no; data
            if packet_num == "EOF":
                send_pck((seeder, discover_port), "ACKEOF")
                break
            received_file.append("".join(data.decode().split(";")[1]))
            if(index == int(packet_num)): # if we received the chunk in order
                packet = "ACK;"+ str(rwnd)+";"+ packet_num
                send_pck((seeder,discover_port), packet)
                index += 1
        except error as e:
            print("Socket error ", e)
    return received_file

def send_file_to_client(client_ip, client_port, client_file_name, rec_wnd):
    socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    socket.bind(("", 3500))
    # Start connection
    # Wait for ACK
    # Set rwnd
    file = open("./" + client_file_name, "rb")
    file_size = getSize(file)
    chunk_number = math.ceil(file_size / 1500.0)
    # Start at chunk index 0
    chunk_index = 0
    in_flight = 0
    # Set timeout for socket
    socket.settimeout(1)
    # Start sending the chunk starting at index 0.
    send_Notfinished = True
    total_sent_packet = 0
    while (True):
        # Send rwnd number of chunks
        while (in_flight < rec_rwnd and send_Notfinished):
            if (chunk_index + in_flight < chunk_number):
                to_send = file.read(1500*chunk_index)
                msg = str(chunk_index + in_flight) + ";" + to_send.decode())
                send_pck((client_ip, client_port), msg)
                in_flight += 1
                total_sent_packet += 1
            if (total_sent_packet == chunk_number):
                send_Notfinished = False
                socket.sendto(b'EOF', (client_ip, client_port))
                break
        # Wait for ACK
        try:
            data, addr = socket.recvfrom(4096)
            if data.decode().split(";")[0] == "ACK":
                #print("Got ACK")
                rec_rwnd = int(data.decode().split(";")[1])
                chunk_index = int(data.decode().split(";")[2]) + 1
                #print(rec_rwnd, chunk_index)
                in_flight -= 1
            if data.decode().split(";")[0] == "ACKEOF":
                return
        except s.timeout as e:
            print("Try to send again")
            in_flight = 0
        except s.error as e:
            print("Socket error: {}".format(e))

    return True



def getSize(fileobject):
    fileobject.seek(0,2) # move the cursor to the end of the file
    size = fileobject.tell()
    return size

def get_input():
    return stdin.readline().rstrip(" \n\r")

def get_seeders(file_name):
    threads = []
    for user in users:
        recvip = addresses[user]
        file_discover_pck = "2;" + host + ";" + file_name + ";" + recvip + ";"
        print("sending ", file_discover_pck)
        thread = Thread(target=send_pck, args=((recvip, discover_port), file_discover_pck))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def send_discovery():
    print("sending discovery")
    arr = host.split(".")
    arr.pop()
    ip = ".".join(arr)
    threads = []
    for i in range(1, 255):
        recvip = ip + "." + str(i)
        discover_pck = "0;" + host + ";" + host_name + ";" + recvip + ";"
        #print("sending ", discover_pck)
        thread = Thread(target=send_pck, args=((recvip, discover_port), discover_pck))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
#    print("disovery finished")

def send_pck(to, pck):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(1)
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
            print("Got ", discover_pck)
            try:
                mod, senderip, sendername, recvip, recvname = discover_pck.split(";")
            except ValueError:
                print("value error")
#                print("im sad")
#            print(sendername)
            users.append(sendername)
            addresses[sendername] = senderip
            message_list[sendername] = []
            if mod == "0":
                discover_pck = "1;" + host + ";" + host_name + ";" + senderip + ";" + sendername
                client.send(bytes(discover_pck, "utf8"))
                print("Sent ", discover_pck)
            if mod == "2":
                file_name_in_pck = sendername
                print("someone is asking for a file ",file_name_in_pck)
                if senderip == host:
                    global file_to_download
                    file_to_download = file_name_in_pck
                files = subprocess.check_output("ls").decode().split("\n")
                if file_name_in_pck in files:
                    print(file_name_in_pck + " exists")
                    #statinfo = os.path.getsize("./" + sendername)
                    #print(statinfo)
                    file = open("./" + file_name_in_pck, 'rb')
                    print(getSize(file))
                    file_size = getSize(file)
                    file_pck = "3;" + host + ";" + host_name + ";" + file_name_in_pck + ";" + str(file_size)
                    print("################################sending ", file_pck)
                    thread = Thread(target=send_pck, args=((senderip, discover_port), file_pck))
                    threads.append(thread)
                    thread.start()
            if mod == "3":
                print(senderip)
                print("########################GOT MESSAGE TYPE 3")
                if senderip == host:
                    global file_to_download_size
                    file_to_download = file_name_in_pck
                    file_to_download_size = "put file size here"
                if senderip not in seeders:
                    seeders.append(senderip)
            if mod == "6":
              send_pck((senderip, 3500), "7;Start;;;")
            if mod == "8":
              rwnd = senderip
              send_file_to_client()
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

def listen_seeders():
  with socket(AF_INET, SOCK_DGRAM) as s:
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.bind(("", discover_port))
    while 1:
      message , address = s.recvfrom(1024);
      print(message);
      message = message.decode("utf-8");
      message = message.split(";")
      messageType = message[0]
      fileName = message[1]
      senderIP = message[2]
      senderPort = message[3]
      if int(messageType) == 0:
        response = "1;" + host
        print(senderIP + " RESPONDED")
        s.sendto(response.encode(),(address))

def discover_seeders():
    message = "0;;" + host + ";;"
    destination = ('<broadcast>', discover_port)
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    try:
      s.sendto(message.encode(), destination)
      response , address = s.recvfrom(5000)
      response = response.decode("utf-8");
      response = response.split(";")
      senderIP = response[1]
      print(response)
      s.close()
    except Exception as e:
      print(e)
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

seeders = []
file_to_download = "(No file selected)"
file_to_download_size = 0

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
threads.append(Thread(target=listen_seeders))
for t in threads:
    t.start()

while True:
    print("1. Online users")
    print("2. Message rooms")
    print("3. Discovery")
    print("4. Discover seeders")
    print("5. Get file", file_to_download)
    print("6. Exit")
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
        print("Please enter a file name")
        file_name = get_input()
        Thread(target=get_seeders, args=(file_name,)).start()
    elif input == "5":
        print("start downloading file, write func for it..")
        print("will ask files from: ")
        for ip in seeders:
            print(ip)
        get_file_from_seeders()
    elif input == "6":
        os._exit(0)
    else:
        continue

# Ending the process
for t in threads:
    t.join()
msg_server.close()
discover_server.close()