import Tkinter as tk

border_width = 9
border_height = 9


def send_ready():
    """
    This method sends server a message when player is ready to start the game
    :return: Method returns nothing
    """
    print "Ready sent"


buttons_player = []


def player_board_fn(x, y):
    """
    This method is a handler of buttons in player's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    print "On player Board " + str(x) + " , " + str(y)
    buttons_player[x][y]['state'] = 'disabled'


buttons_enemy = []


def enemy_board_fn(x, y):
    """
    This method is a handler of buttons in enemy's board.
    :param x: x co-ordinate of location
    :param y: x co-ordinate of location
    :return: Nothing
    """
    print "On enemy Board " + str(x) + " , " + str(y)


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
b = tk.Button(fr_2, text=" Ready ", command=send_ready)
b.pack()

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
