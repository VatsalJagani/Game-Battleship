import Tkinter as tk
import socket
import sys
import threading

border_width = 10
border_height = 10
PLAYER = '1'
ENEMY = '2'

BUFFER = 512
ip_of_server = '172.16.4.94'
port = 1234
clientsocket = None

buttons_player = []
buttons_enemy = []
ready_button = None
l_game_status = None
l_player_status = None
l_enemy_status = None
ship_locations = '11|12,13'  # This is the pattern which server accepts as ship's location


def disable_ready():
    """
    This method disables ready button
    :return: Nothing
    """
    ready_button['state'] = 'disabled'


def enable_ready():
    """
    This method enables ready button
    :return: Nothing
    """
    ready_button['state'] = 'normal'


def disable_player_grid():
    """
    This method disables all buttons in player's grid
    :return: Nothing
    """
    for x in range(border_height):
        for y in range(border_width):
            buttons_player[x][y]['state'] = 'disabled'


def enable_player_grid():
    """
    This method enables all buttons in player's grid
    :return: Nothing
    """
    for x in range(border_height):
        for y in range(border_width):
            buttons_player[x][y]['state'] = 'normal'


def disable_enemy_grid():
    """
    This method disables all buttons in enemy's grid
    :return: Nothing
    """
    for x in range(border_height):
        for y in range(border_width):
            buttons_enemy[x][y]['state'] = 'disabled'


def enable_enemy_grid():
    """
    This method enables all buttons in enemy's grid
    :return: Nothing
    """
    for x in range(border_height):
        for y in range(border_width):
            buttons_enemy[x][y]['state'] = 'normal'


def getAttackInstruction():
    """
    This method run only once, and receives the instruction from server.
    :return: Nothing
    """
    instruction = clientsocket.recv(BUFFER)
    performOperation(instruction)


def sendInstruction(attackPosition):
    """
    This method sends the attack position to server.
    :param attackPosition: Location to launch the attack.
    :return: Nothing
    """
    clientsocket.send(attackPosition)


def checkOperationToPerform():
    """
    This method receive two messages form server and send to performOperation method to perform task accordingly.
    :return: Nothing
    """
    while True:
        hit_or_miss = clientsocket.recv(BUFFER)
        instruction = clientsocket.recv(BUFFER)
        performOperation(hit_or_miss)
        performOperation(instruction)


def performOperation(instruction):
    """
    This method check instruction and perform task accordingly.
    :param instruction: Task to perform
    :return: Nothing
    """
    if instruction == 'attack':
        # Player get chance to attack
        # Get location from GUI and sends to server.
        l_game_status.config(text="    Attack, It's your turn    ")
        enable_enemy_grid()
    elif instruction == 'wait':
        # It's player's opponent turn to attack.
        l_game_status.config(text="    Wait It's your enemy's turn    ")
        disable_enemy_grid()
    # This instruction is received from server informing where hit or miss has occurred
    # instruction starts with whether hit or miss has occurred
    # followed by a number indicating which grid at client side should be reflected
    # (2 for opponent 1 for player) followed by 2 numbers indicating position of attack
    # followed by 2 numbers indicating number of ships sank of player 1(player) and 2(enemy) respectively
    elif instruction.startswith('hit'):
        # Change GUI accordingly to RED as it HIT.
        # Check if this is HIT on player or opponent
        if instruction[3] == PLAYER:
            # Change player's board
            x = int(instruction[4])
            y = int(instruction[5])
            buttons_player[x][y].configure(bg='#fc0000')
        else:
            # Change enemy's board
            x = int(instruction[4])
            y = int(instruction[5])
            buttons_enemy[x][y].configure(bg='#fc0000')
        l_player_status.configure(text="Your Ship sank - " + instruction[6])
        l_enemy_status.configure(text="Enemy's Ship sank - " + instruction[7])
    elif instruction.startswith('miss'):
        # Change GUI accordingly to LIGHT BLUE as it's MISS.
        # Check if this is MISS on player or opponent
        if instruction[4] == PLAYER:
            # Changes in player board
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_player[x][y].configure(bg='#00fce7')
        else:
            # Change enemy's board
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_enemy[x][y].configure(bg='#00fce7')
        l_player_status.configure(text="Your Ship sank - " + instruction[7])
        l_enemy_status.configure(text="Enemy's Ship sank - " + instruction[8])
    elif instruction == 'win':
        # Game over and player wins the game
        l_game_status.config(text="    You won  !!!   ")
        clientsocket.close()
        disable_enemy_grid()   # Disables enemy grid when player won.
        return
    elif instruction == 'lost':
        # Game over and player lost the game
        l_game_status.config(text="   Sorry, You lost the game, Try again.  ")
        clientsocket.close()
        return


# Connection Establishment with server
try:
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip_of_server, port))
except:
    print "Connection cannot be established.."
    sys.exit()

# Ready message from server
server_ready = clientsocket.recv(BUFFER)


def send_ready():
    """
    This method sends server a message when player is ready to start the game
    :return: Method returns nothing
    """
    clientsocket.send(ship_locations)
    disable_ready()
    disable_player_grid()
    my_thread = threading.Thread(target=getAttackInstruction)
    my_thread.start()
    my_thread = threading.Thread(target=checkOperationToPerform)
    my_thread.start()


def player_board_fn(x, y):
    """
    This method is a handler of buttons in player's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    # Settle ships here
    pass


def enemy_board_fn(x, y):
    """
    This method is a handler of buttons in enemy's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    send_thread = threading.Thread(target=sendInstruction, args=['' + str(x) + str(y)])
    send_thread.start()


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

# Display GUI
root.mainloop()
