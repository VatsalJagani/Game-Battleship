import Tkinter as tk
import socket
import os
import threading

border_width = 10
border_height = 10
PLAYER = '1'
ENEMY = '2'
ready_flag = False
BUFFER = 512
ip_of_server = '127.0.0.1'
port = 1234
clientsocket = None
shipsettleflag = 3
buttons_player = []
buttons_enemy = []
ready_button = None
l_game_status = None
l_player_status = None
l_enemy_status = None
ship_locations = ''  # This is the pattern which server accepts as ship's location
direction = 'h'
button_disable_flags = []

button_color = ""
bg_color = '#9d99fc'
game_status_color = '#000000'
player_status_color = '#a50415'
player_color = '#043a04'
game_name_color = '#0404d8'
hit_color = '#fc0000'
miss_color = '#00fce7'
ship_color = '#0000ff'

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
    global button_color
    for x in range(border_height):
        for y in range(border_width):
            buttons_player[x][y].configure(background=button_color)
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


def enable_enemy_grid_partialy():
    """
    This method enables does not enables buttons on which attak has been already launched.
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
    global clientsocket
    instruction = clientsocket.recv(BUFFER)
    performOperation(instruction)


def sendInstruction(attackPosition):
    """
    This method sends the attack position to server.
    :param attackPosition: Location to launch the attack.
    :return: Nothing
    """
    global clientsocket
    clientsocket.send(attackPosition)


def checkOperationToPerform():
    """
    This method receive two messages form server and send to performOperation method to perform task accordingly.
    :return: Nothing
    """
    global clientsocket
    while True:
        try:
            hit_or_miss = clientsocket.recv(BUFFER)
            instruction = clientsocket.recv(BUFFER)
            performOperation(hit_or_miss)
            performOperation(instruction)
        except:
            pass
            # Game Over Here


def performOperation(instruction):
    """
    This method check instruction and perform task accordingly.
    :param instruction: Task to perform
    :return: Nothing
    """
    global clientsocket
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
            buttons_player[x][y].configure(bg=hit_color)
        else:
            # Change enemy's board
            x = int(instruction[4])
            y = int(instruction[5])
            buttons_enemy[x][y].configure(bg=hit_color)
        l_player_status.configure(text="Your Ship destroyed - " + instruction[6])
        l_enemy_status.configure(text="Enemy's Ship destroyed - " + instruction[7])
    elif instruction.startswith('miss'):
        # Change GUI accordingly to LIGHT BLUE as it's MISS.
        # Check if this is MISS on player or opponent
        if instruction[4] == PLAYER:
            # Changes in player board
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_player[x][y].configure(bg=miss_color)
        else:
            # Change enemy's board
            x = int(instruction[5])
            y = int(instruction[6])
            buttons_enemy[x][y].configure(bg=miss_color)
        l_player_status.configure(text="Your Ship destroyed - " + instruction[7])
        l_enemy_status.configure(text="Enemy's Ship destroyed - " + instruction[8])
    elif instruction == 'win':
        # Game over and player wins the game
        l_game_status.config(text="    You won  !!!   ")
        clientsocket.close()
        disable_enemy_grid()  # Disables enemy grid when player won.
        return
    elif instruction == 'lost':
        # Game over and player lost the game
        l_game_status.config(text="   Sorry, You lost the game, Try again.  ")
        clientsocket.close()
        return


def send_ready():
    """
    This method sends server a message when player is ready to start the game
    :return: Method returns nothing
    """
    global clientsocket, horizontal_button, vertical_button, ship_locations, reset_button
    if ready_flag == False:
        l_game_status.config(text="Select ship positions")
        return
    horizontal_button['state'] = 'disabled'
    vertical_button['state'] = 'disabled'
    reset_button['state'] = 'disabled'
    clientsocket.send(ship_locations)
    disable_ready()
    l_game_status.configure(text='Waiting for oppenent to be ready!')
    disable_player_grid()
    my_thread = threading.Thread(target=getAttackInstruction)
    my_thread.start()
    my_thread = threading.Thread(target=checkOperationToPerform)
    my_thread.start()


def resetshipposition():
    """
    This function resets ship locations
    :return:
    """
    global shipsettleflag, ready_flag, l_game_status, ship_locations
    ship_locations = ""
    ready_flag = False
    shipsettleflag = 3
    l_game_status.config(text='Select ship of 4 blocks')
    enable_player_grid()


def player_board_fn(x, y):
    """
    This method is a handler of buttons in player's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    # Settle ships here
    global direction
    if direction == 'h':
        sethorizontalposition(x, y)
    if direction == 'v':
        setverticalposition(x, y)


def setverticalposition(x, y):
    """
    This function sets ships positions vertically based on x & y
    :param x:
    :param y:
    :return:
    """
    global shipsettleflag
    global ready_flag
    global ship_locations

    # validates x & y and sets 4 block of ship vertically
    if shipsettleflag == 3:
        if x + 3 > 9 or y > 9:
            return
        shipsettleflag = shipsettleflag - 1
        l_game_status.config(text="Select ship of 3 blocks")
        for i in range(4):
            if i == 3:
                ship_locations = ship_locations + str(x + i) + str(y) + '|'
            else:
                ship_locations = ship_locations + str(x + i) + str(y) + ','
            buttons_player[x + i][y].configure(bg='#0000ff')
            buttons_player[x + i][y]['state'] = 'disabled'
    # validates x & y and sets 3 block of ship vertically
    elif shipsettleflag == 2:
        if x + 2 > 9 or y > 9:
            return
        shipsettleflag = shipsettleflag - 1
        l_game_status.config(text="Select ship of 1 blocks")
        for i in range(3):
            if i == 2:
                ship_locations = ship_locations + str(x + i) + str(y) + '|'
            else:
                ship_locations = ship_locations + str(x + i) + str(y) + ','
            buttons_player[x + i][y].configure(bg=ship_color)
            buttons_player[x + i][y]['state'] = 'disabled'
    # sets 1 block of ship vertically
    elif shipsettleflag == 1:
        shipsettleflag = shipsettleflag - 1
        ship_locations = ship_locations + str(x) + str(y)
        l_game_status.config(text="Ready")
        buttons_player[x][y].configure(bg=ship_color)
        buttons_player[x][y]['state'] = 'disabled'
        ready_flag = True


def sethorizontalposition(x, y):
    """
    This function sets ships positions horizontally based on x & y
    :param x:
    :param y:
    :return:
    """
    global shipsettleflag
    global ready_flag
    global ship_locations

    # validates x & y and sets 4 block of ship vertically
    if shipsettleflag == 3:
        if x > 9 or y + 3 > 9:
            return
        shipsettleflag = shipsettleflag - 1
        l_game_status.config(text="Select ship of 3 blocks")
        for i in range(4):
            if i == 3:
                ship_locations = ship_locations + str(x) + str(y + i) + '|'
            else:
                ship_locations = ship_locations + str(x) + str(y + i) + ','
            buttons_player[x][y + i].configure(bg='#0000ff')
            buttons_player[x][y + i]['state'] = 'disabled'
    # validates x & y and sets 3 block of ship vertically
    elif shipsettleflag == 2:
        if x > 9 or y + 2 > 9:
            return
        shipsettleflag = shipsettleflag - 1
        l_game_status.config(text="Select ship of 1 blocks")
        for i in range(3):
            if i == 2:
                ship_locations = ship_locations + str(x) + str(y + i) + '|'
            else:
                ship_locations = ship_locations + str(x) + str(y + i) + ','
            buttons_player[x][y + i].configure(bg='#0000ff')
            buttons_player[x][y + i]['state'] = 'disabled'
    # sets 1 block of ship vertically
    elif shipsettleflag == 1:
        shipsettleflag = shipsettleflag - 1
        ship_locations = ship_locations + str(x) + str(y)
        l_game_status.config(text="Ready")
        buttons_player[x][y].configure(bg='#0000ff')
        buttons_player[x][y]['state'] = 'disabled'
        ready_flag = True


def setvertical():
    """
    sets direction to vertical to set ship positions
    :return:
    """
    global horizontal_button, direction
    direction = 'v'
    vertical_button['state'] = 'disabled'
    horizontal_button['state'] = 'normal'


def sethorizontal():
    """
    sets direction to horizontal to set ship positions
    :return:
    """
    global vertical_button, direction
    horizontal_button['state'] = 'disabled'
    vertical_button['state'] = 'normal'
    direction = 'h'


def enemy_board_fn(x, y):
    """
    This method is a handler of buttons in enemy's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    global button_disable_flags
    if button_disable_flags[x][y] == False:
        button_disable_flags[x][y] = True
        send_thread = threading.Thread(target=sendInstruction, args=['' + str(x) + str(y)])
        send_thread.start()


def connect_to_server():
    """
    Connection Establishment with server
    :return: Nothing
    """
    global clientsocket
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((ip_of_server, port))
        # Set waiting message
        l_game_status.configure(text=' Connecting to your opponent...')

        # Ready message from server
        server_ready = clientsocket.recv(BUFFER)
        # Set game status to select ship position
        enable_player_grid()
        enable_ready()
        l_game_status.config(text="Select ship of 4 blocks")
    except Exception as e:
        print e.message
        l_game_status.configure(text="Connection cannot be established..")


# GUI rendering
root = tk.Tk()
root.title("Battleship")
fr_main = tk.Frame(root, bg=bg_color)
fr_main.pack()

# Temp button for getting default background color
button_color = tk.Button(root).cget('background')

fr_upper = tk.Frame(fr_main, bg=bg_color)
fr_upper.grid(row=0, column=0)

# Statuses
l_player_status = tk.Label(fr_upper, text="", font=("Helvetica", 15), bg=bg_color, fg=player_status_color)
l_enemy_status = tk.Label(fr_upper, text="", font=("Helvetica", 15), bg=bg_color, fg=player_status_color)
l_game_status = tk.Label(fr_upper, text="Game Status", font=("Helvetica", 15), bg=bg_color, fg=game_status_color)

l_player_status.grid(row=0, column=0)
l_game_status.grid(row=0, column=2, columnspan=2, pady=3, padx=10)
l_enemy_status.grid(row=0, column=5)

fr_lower = tk.Frame(fr_main, bg=bg_color)
fr_lower.grid(row=1, column=0, rowspan=10)

fr_1 = tk.Frame(fr_lower, bg=bg_color)
fr_1.grid(row=0, column=0, columnspan=5, padx=10)

# Rendering player's board
for x in range(border_height):
    temp_buttons = []
    for y in range(border_width):
        b = tk.Button(fr_1, command=lambda x=x, y=y: player_board_fn(x, y), text=" ", height=2, width=3)
        b.grid(row=x, column=y)
        temp_buttons.append(b)
    buttons_player.append(temp_buttons)
disable_player_grid()

fr_2 = tk.Frame(fr_lower, bg=bg_color)
fr_2.grid(row=0, column=5, columnspan=2)

ready_button = tk.Button(fr_2, text=" Ready ", height=3, width=12, command=send_ready)
ready_button.grid(row=0, column=0, rowspan=4, pady=100, padx=10)
disable_ready()
horizontal_button = tk.Button(fr_2, text="Horizontal", height=2, width=10, command=sethorizontal)
horizontal_button.grid(row=4, column=0, padx=15, pady=1)
horizontal_button['state'] = 'disabled'
vertical_button = tk.Button(fr_2, text="Vertical", height=2, width=10, command=setvertical)
vertical_button.grid(row=5, column=0, padx=15, pady=1)
reset_button = tk.Button(fr_2, text="Reset", height=2, width=10, command=resetshipposition)
reset_button.grid(row=6, column=0, padx=15, pady=5)
fr_3 = tk.Frame(fr_lower, bg=bg_color)
fr_3.grid(row=0, column=7, columnspan=5, padx=10)

# Rendering enemy's board
for x in range(border_height):
    temp_buttons = []
    temp_flag_list = []
    for y in range(border_width):
        b = tk.Button(fr_3, command=lambda x=x, y=y: enemy_board_fn(x, y), text=" ", height=2, width=3)
        b.grid(row=x, column=y)
        temp_buttons.append(b)
        temp_flag_list.append(False)
    buttons_enemy.append(temp_buttons)
    button_disable_flags.append(temp_flag_list)
disable_enemy_grid()

fr_bottom = tk.Frame(fr_main, bg=bg_color)
fr_bottom.grid(row=11, column=0)

# Statuses
l_player = tk.Label(fr_bottom, text="Your Realm", font=("Helvetica", 15), bg=bg_color, fg=player_color)
l_enemy = tk.Label(fr_bottom, text=" Enemy's Realm", font=("Helvetica", 15), bg=bg_color, fg=player_color)
l_game_name = tk.Label(fr_bottom, text="--- BattleShip ---  \t\t", font=("Helvetica", 20), bg=bg_color,
                       fg=game_name_color)

l_player.grid(row=0, column=0)
l_game_name.grid(row=0, column=2, columnspan=2, pady=3, padx=10)
l_enemy.grid(row=0, column=5)

# Information
tk.Button(fr_bottom, text=" ", height=2, width=3, bg=ship_color).grid(row=1, column=0)
tk.Button(fr_bottom, text=" ", height=2, width=3, bg=hit_color).grid(row=2, column=0)
tk.Button(fr_bottom, text=" ", height=2, width=3, bg=miss_color).grid(row=3, column=0)
tk.Label(fr_bottom, text="Ship Color", font=("Helvetica", 10), bg=bg_color).grid(row=1, column=1)
tk.Label(fr_bottom, text="HIT Color", font=("Helvetica", 10), bg=bg_color).grid(row=2, column=1)
tk.Label(fr_bottom, text="MISS Color", font=("Helvetica", 10), bg=bg_color).grid(row=3, column=1)

# Connect to server
connection = threading.Thread(target=connect_to_server)
connection.start()

# Display GUI
root.resizable(width=False, height=False)
root.mainloop()
os._exit(0)
