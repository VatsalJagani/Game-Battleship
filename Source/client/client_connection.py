import socket
import sys

ip_of_server = '172.16.4.94'
port = 1234
try:
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip_of_server, port))
except:
    print "Connection cannot be established.."
    sys.exit()

server_ready = clientsocket.recv(2048)
if server_ready == 'ready':
    # Arrage ships on the board and send location to server on clicking Ready button on GUI.
    ship_locations = '11,22,33|44,55|99'  # This is the pattern which server accepts as ship's location
    clientsocket.send(ship_locations)

    while True:
        instruction = clientsocket.recv(2048)
        if instruction == 'attack':
            # Player get chance to attack
            # Get location from GUI and sends to server
            pass
        elif instruction == 'wait':
            # It's player's opponent
            pass
        elif instruction == 'win':
            # Game over and player wins the game
            pass
        elif instruction == 'lost':
            # Game over and player lost the game
            pass
        else:
            continue
