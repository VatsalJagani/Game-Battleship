import Tkinter as tk
import socket
import sys
import threading

border_width = 9
border_height = 9
PLAYER = '1'
ENEMY = '2'
BUFFER = 512
ip_of_server = '172.16.4.94'
port = 1234
clientsocket = None
buttons_player = []
buttons_enemy = []
ready_button = None
ship_locations = '11,22,33|44,55|99'  # This is the pattern which server accepts as ship's location


# GUI event method
def disable_ready():
    ready_button['state'] = 'disabled'

# GUI event method
def disable_player_grid():
    for x in range(border_height):
        for y in range(border_width):
            buttons_player[x][y]['state'] = 'disabled'

# GUI event method
def enable_player_grid():
    for x in range(border_height):
        for y in range(border_width):
            buttons_player[x][y]['state'] = 'normal'

# GUI event method
def disable_enemy_grid():
    for x in range(border_height):
        for y in range(border_width):
            buttons_enemy[x][y]['state'] = 'disabled'

# GUI event method
def enable_enemy_grid():
    for x in range(border_height):
        for y in range(border_width):
            buttons_enemy[x][y]['state'] = 'normal'


def checkOperationToPerform():
    global l_game_status
    instruction = clientsocket.recv(BUFFER)
    if instruction == 'attack':
        # Player get chance to attack
        # Get location from GUI and sends to server
        l_game_status.config(text = "    Attak, It's your turn    ")
        enable_enemy_grid()
    elif instruction == 'wait':
        # It's player's opponent
        # Disable GUI buttons
        l_game_status.config(text = "    Wait It's your enemy's turn    ")
        disable_enemy_grid()
        my_thread = threading.Thread(target=checkOperationToPerform)
        my_thread.start()
    elif instruction.startswith('hit'):
        # Change GUI accordingly
        if instruction[3] == PLAYER:
            # Changes in player board
            print "HIT in player"
            x = int(instruction[4])
            y = int(instruction[5])
            buttons_player[x][y].configure(bg='#fc0000')
        else:
            # Change enemy's board
            print "HIT in enemy"
            x = int(instruction[4])
            y = int(instruction[5])
            buttons_enemy[x][y].configure(bg='#fc0000')
        checkOperationToPerform()
    elif instruction.startswith('miss'):
        # Change GUI accordingly
        if instruction[4] == PLAYER:
            # Changes in player board
            print "MISS in player"
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_player[x][y].configure(bg='#00fce7')
        else:
            # Change enemy's board
            print "MISS in enemy"
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_enemy[x][y].configure(bg='#00fce7')
        checkOperationToPerform()
    elif instruction == 'win':
        # Game over and player wins the game
        l_game_status.config(text = "    You won  !!! ")
        clientsocket.close()
        return
    elif instruction == 'lost':
        # Game over and player lost the game
        l_game_status.config(text = "    Sorry, You lost the game, Try again.   ")
        clientsocket.close()
        return

# Connection Establishment
try:
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip_of_server, port))
except:
    print "Connection cannot be established.."
    sys.exit()

server_ready = clientsocket.recv(BUFFER)   # Ready message from server





# GUI Event method
def send_ready():
    """
    This method sends server a message when player is ready to start the game
    :return: Method returns nothing
    """
    ship_locations = '11,12,13|51,61,71,81'  # This is the pattern which server accepts as ship's location
    clientsocket.send(ship_locations)
    disable_ready()
    disable_player_grid()
    my_thread = threading.Thread(target=checkOperationToPerform)
    my_thread.start()

# GUI event method
def player_board_fn(x, y):
    """
    This method is a handler of buttons in player's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    print "On enemy Board " + str(x) + " , " + str(y)


# GUI event method
def enemy_board_fn(x, y):
    """
    This method is a handler of buttons in enemy's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    clientsocket.send('' + str(x) + str(y))
    print "On enemy Board " + str(x) + " , " + str(y)
    checkOperationToPerform()



# GUI rendering
root = tk.Tk()
root.title("Battleship")
fr_main = tk.Frame(root)
fr_main.pack()

fr_upper = tk.Frame(fr_main)
fr_upper.grid(row=0, column=0)

# Statuses
l_player_status = tk.Label(fr_upper, text="Player Status")
l_enemy_status = tk.Label(fr_upper, text="Enemy Status")
l_game_status = tk.Label(fr_upper, text="Game Status")

l_player_status.grid(row=0, column=0)
l_enemy_status.grid(row=0, column=2)
l_game_status.grid(row=0, column=1)

fr_lower = tk.Frame(fr_main)
fr_lower.grid(row=1, column=0, rowspan=10)

fr_1 = tk.Frame(fr_lower)
fr_1.grid(row=0, column=0, columnspan=5)

# Rendering player's board
for x in range(border_height):
    temp_buttons = []
    for y in range(border_width):
        b = tk.Button(fr_1, command=lambda x=x, y=y: player_board_fn(x, y), text="   ")
        b.grid(row=x, column=y)
        temp_buttons.append(b)
    buttons_player.append(temp_buttons)

fr_2 = tk.Frame(fr_lower)
fr_2.grid(row=0, column=5)
ready_button = tk.Button(fr_2, text=" Ready ", command=send_ready)
ready_button.pack()

fr_3 = tk.Frame(fr_lower)
fr_3.grid(row=0, column=6, columnspan=5)

# Rendering enemy's board
for x in range(border_height):
    temp_buttons = []
    for y in range(border_width):
        b = tk.Button(fr_3, command=lambda x=x, y=y: enemy_board_fn(x, y), text="   ")
        b.grid(row=x, column=y)
        temp_buttons.append(b)
    buttons_enemy.append(temp_buttons)

root.mainloop()