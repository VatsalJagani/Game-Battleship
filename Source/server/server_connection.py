import socket
import threading


class Game:
    """
    Object of this class is used to store every new game(pair of two player.)
    """
    def getshiplocation(self, conn, player):
        """
        receives positions of ship locations from clients and adds it to appropriate player's list
        client must use unique format to send ship locations, '|' sign is used to separate ships
        ',' is used to separate coordinates of particular ship
        ex- 1,2,3|4,5|9
        represents 3 ships having coordinates (1,2,3),(4,5) and (9)
        :param conn:
        :param player:
        :return:
        """
        self.player1List = []  # contains ship positions of player 1
        self.player2List = []  # contains ship positions of player 2
        positions = ''
        try:
            positions = str(conn.recv(512)).strip()
        except:
            print "Error : Player is not reachable."
            return
        positionlist = positions.split("|")
        if player == 1:
            for i in positionlist:
                self.player1List.append(i.split(","))
        else:
            for i in positionlist:
                self.player2List.append(i.split(","))
        self.no_ship = len(self.player1List)

    def establishconnection(self, serversocket):
        """
        waits for both players to get connected to server and sends responses to both clients when both are ready
        :param serversocket:
        :return:
        """
        self.playerconn1, addr = serversocket.accept()
        self.playerconn2, addr = serversocket.accept()
        self.sendready()
        print "New Game Started."


    def sendready(self):
        """
        sends ready message to both clients so that they can proceed with further doings
        :return:
        """
        self.playerconn1.send('ready')
        self.playerconn2.send('ready')


    def closeconn(self):
        """
        This function closes connection of both the player when any game is over.
        :return: Noting
        """
        self.game_running_flag = False
        self.playerconn1.close()
        self.playerconn2.close()

    def checkwin(self, player):
        """
        checks game winning condition
        :param player:
        :return: Boolean flag, whether game is over or not.
        """
        if player == 1:
            if len(self.player2List) == 0:
                self.playerconn1.send("win")
                self.playerconn2.send("lost")
                self.closeconn()
                return True
        else:
            if len(self.player1List) == 0:
                self.playerconn1.send("lost")
                self.playerconn2.send("win")
                self.closeconn()
                return True
        return False


    def checkhit(self, pos, player):
        """
        checks hit at attack location or not for player
        :param pos:
        :param player:
        :return: Boolean flag whether attack is HIT ir not.
        """
        if player == 1:
            for i in self.player2List:
                if pos in i:
                    i.remove(pos)
                    if len(i) == 0:
                        self.player2List.remove(i)
                    return True
            return False
        else:
            for i in self.player1List:
                if pos in i:
                    i.remove(pos)
                    if len(i) == 0:
                        self.player1List.remove(i)
                    return True
            return False


    def getattackposition(self, conn, player):
        """
        Gets attack position from client and sends appropriate instructions to clients
        :param conn: Connection object fot player.
        :param player: For which player attack is launched.
        :return: Nothing
        """
        self.shipsankplayer1 = "0"
        self.shipsankplayer2 = "0"
        try:
            while True:
                pos = conn.recv(512)
                if self.game_running_flag == False:
                    return
                if player == 1:
                    if self.checkhit(pos, player):
                        # This instruction is sent to both client informing where hit or miss has occurred
                        # instruction starts with whether hit or miss has occurred
                        # followed by a number indicating which grid at client side should be reflected
                        # (2 for opponent 1 for player) followed by 2 numbers indicating position of attack
                        # followed by 2 numbers indicating number of ships sank of player and opponent respectively
                        self.shipsankplayer2=str(self.no_ship-len(self.player2List))
                        self.playerconn1.send("hit2" + pos+self.shipsankplayer1+self.shipsankplayer2)
                        self.playerconn2.send("hit1" + pos+self.shipsankplayer2+self.shipsankplayer1)
                        if self.checkwin(player):
                            return
                        self.playerconn1.send("attack")
                        self.playerconn2.send("wait")
                    else:
                        self.playerconn1.send("miss2" + pos+self.shipsankplayer1+self.shipsankplayer2)
                        self.playerconn2.send("miss1" + pos+self.shipsankplayer2+self.shipsankplayer1)
                        self.playerconn1.send("wait")
                        self.playerconn2.send("attack")
                else:
                    if self.checkhit(pos, player):
                        self.shipsankplayer1 = str(self.no_ship - len(self.player1List))
                        self.playerconn1.send("hit1" + pos+self.shipsankplayer1+self.shipsankplayer2)
                        self.playerconn2.send("hit2" + pos+self.shipsankplayer2+self.shipsankplayer1)
                        if self.checkwin(player):
                            return
                        self.playerconn1.send("wait")
                        self.playerconn2.send("attack")
                    else:
                        self.playerconn1.send("miss1" + pos+self.shipsankplayer1+self.shipsankplayer2)
                        self.playerconn2.send("miss2" + pos+self.shipsankplayer2+self.shipsankplayer1)
                        self.playerconn1.send("attack")
                        self.playerconn2.send("wait")
        except Exception as e:
            print e.message
            print "Error : Player forcefully terminated connection."

    def __init__(self, serversocket):
        """
        This method creates new game when ever two new player connects
        """
        try:
            self.establishconnection(serversocket)  # establishing connection to both clients
            game_thread = threading.Thread(target=self.start_game)  # New Game started.
            game_thread.start()
        except Exception as e:
            print e.message

    def start_game(self):
        """
        Initialize Game in seperate thread.
        :param serversocket: Server Socket
        :return: Nothing
        """
        try:
            t1 = threading.Thread(target=self.getshiplocation,
                                  args=[self.playerconn1, 1])  # Creates threads for both players which wait for
            t2 = threading.Thread(target=self.getshiplocation, args=[self.playerconn2, 2])  # client to send ship locations
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.game_running_flag = True
            self.playerconn1.send("attack")  # Sends attack instruction to player 1
            self.playerconn2.send("wait")  # Sends wait instruction to player 2
            t1 = threading.Thread(target=self.getattackposition,
                                  args=[self.playerconn1, 1])  # Creates threads for both players which wait for
            t2 = threading.Thread(target=self.getattackposition, args=[self.playerconn2, 2])  # client to send attack location
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            print "Game Over"
        except Exception as e:
            print e.message


# Server runs continuously to serve multi-game functionality.
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates a server which listens to port 1234
    serversocket.bind(('0.0.0.0', 1234))
    serversocket.listen(0)
    print "server started.."
    while True:
        g = Game(serversocket)
except Exception as e:
    print "Server cannot be started, specified port may already in use."
    print e.message
finally:
    print "server stopped."