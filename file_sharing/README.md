# Python Chat App - CMPE 487

Run server.py with a python3 interpreter `python3 server.py`

## How to Use

The menu has 4 options
1. Online users: Shows a list of users that have been online since the program was run. Includes you.
7. Message rooms: Opens message room menu. First you select which user you want to message with. This opens up the message room. You cannot see messages that are sent after you open the message room.
You can go back to the menu by inputing `{q}`
93. Discovery: Sends discovery packets to everyone in the background
6. Exit: Exits the program


Message types:
Discovery message:
0;HOST_IP; HOST_NAME;;

Accept Discovery message:
1;HOST_IP; HOST_NAME; RECEIVER_IP; RECEIVER_NAME

Ask for file message:
2;HOST_IP;FILE_NAME;RECEIVER_IP;

File exists message:
3;HOST_IP;HOST_NAME;FILE_NAME;FILE_SIZE