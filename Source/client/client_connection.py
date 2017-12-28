# This file is for testing server-client connection and message transfer, later this code will combine with GUI code.
import socket
import sys

PLAYER = '1'
ENEMY = '2'
BUFFER = 512

ip_of_server = '172.16.4.94'
port = 1234

# Connection Establishment
try:
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip_of_server, port))
except:
    print "Connection cannot be established.."
    sys.exit()

server_ready = clientsocket.recv(BUFFER)
if server_ready == 'ready':
    # Arrage ships on the board and send location to server on clicking Ready button on GUI.
    ship_locations = '11,22,33|44,55|99'  # This is the pattern which server accepts as ship's location
    clientsocket.send(ship_locations)

    while True:
        instruction = clientsocket.recv(BUFFER)
        if instruction == 'attack':
            # Player get chance to attack
            # Get location from GUI and sends to server
            print "Attack : "
            x = input('X : ')
            y = input('Y : ')
            # Here x & y is co-ordinate of attack location
            clientsocket.send('' + str(x) + str(y))
        elif instruction == 'wait':
            # It's player's opponent
            # Disable GUI buttons
            print "Wait"
        elif instruction.startswith('hit'):
            # Change GUI accordingly
            if instruction[3] == PLAYER:
                # Changes in player board
                print "HIT in player"
            else:
                # Change enemy's board
                print "HIT in enemy"
        elif instruction.startswith('miss'):
            # Change GUI accordingly
            if instruction[4] == PLAYER:
                # Changes in player board
                print "MISS in player"
            else:
                # Change enemy's board
                print "MISS in enemy"
        elif instruction == 'win':
            # Game over and player wins the game
            print "Win"
            clientsocket.close()
            break
        elif instruction == 'lost':
            # Game over and player lost the game
            print "Lost"
            clientsocket.close()
            break
        else:
            continue
