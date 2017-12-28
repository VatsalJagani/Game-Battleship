import socket
import threading

game_running_flag = True
playerconn1 = None
playerconn2 = None  # keeps track of connection objects of clients
player1List = []  # contains ship positions of player 1
player2List = []  # contains ship positions of player 2


def getshiplocation(conn, player):
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
    positions = str(conn.recv(512)).strip()
    print positions
    positionlist = positions.split("|")
    if player == 1:
        for i in positionlist:
            player1List.append(i.split(","))
        print player1List
    else:
        for i in positionlist:
            player2List.append(i.split(","))
        print player2List


def establishconnection(serversocket):
    """
    waits for both players to get connected to server and sends responses to both clients when both are ready
    :param serversocket:
    :return:
    """
    global playerconn1
    global playerconn2
    playerconn1, addr = serversocket.accept()
    playerconn2, addr = serversocket.accept()
    sendready()


def sendready():
    """
    sends ready message to both clients so that they can proceed with further doings
    :return:
    """
    playerconn1.send('ready')
    playerconn2.send('ready')


def closeconn():
    global game_running_flag
    game_running_flag = False
    playerconn1.close()
    playerconn2.close()


def checkwin(player):
    """
    checks win condition
    :param player:
    :return:
    """
    if player == 1:
        if len(player2List) == 0:
            playerconn1.send("win")
            playerconn2.send("lost")
            closeconn()
            return True
    else:
        if len(player1List) == 0:
            playerconn1.send("lost")
            playerconn2.send("win")
            closeconn()
            return True
    return False


def checkhit(pos, player):
    """
    checks hit at attack location for player
    :param pos:
    :param player:
    :return:
    """
    if player == 1:
        for i in player2List:
            if pos in i:
                i.remove(pos)
                if len(i) == 0:
                    player2List.remove(i)
                return True
        return False
    else:
        for i in player1List:
            if pos in i:
                i.remove(pos)
                if len(i) == 0:
                    player1List.remove(i)
                return True
        return False


def getattackposition(conn, player):
    """
    Gets attack position from client and sends appropriate instructions to clients
    :param conn:
    :param player:
    :return:
    """
    while True:
        pos = conn.recv(512)
        if game_running_flag == False:
            return
        if player == 1:
            if checkhit(pos, player):
                if checkwin(player):
                    return
                playerconn1.send("hit2" + pos)
                playerconn2.send("hit1" + pos)
                playerconn1.send("attack")
                playerconn2.send("wait")
            else:
                playerconn1.send("miss2" + pos)
                playerconn2.send("miss1" + pos)
                playerconn1.send("wait")
                playerconn2.send("attack")
        else:
            if checkhit(pos, player):
                if checkwin(player):
                    return
                playerconn1.send("hit1" + pos)
                playerconn2.send("hit2" + pos)
                playerconn1.send("wait")
                playerconn2.send("attack")

            else:
                playerconn1.send("miss1" + pos)
                playerconn2.send("miss2" + pos)
                playerconn1.send("attack")
                playerconn2.send("wait")


try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates a server which listens to port 1234
    serversocket.bind(('0.0.0.0', 1234))
    serversocket.listen(0)
    establishconnection(serversocket)  # establishing connection to both clients
    t1 = threading.Thread(target=getshiplocation,
                          args=[playerconn1, 1])  # Creates threads for both players which wait for
    t2 = threading.Thread(target=getshiplocation, args=[playerconn2, 2])  # client to send ship locations
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    playerconn1.send("attack")  # Sends attack instruction to player 1
    playerconn2.send("wait")  # Sends wait instruction to player 2
    t1 = threading.Thread(target=getattackposition,
                          args=[playerconn1, 1])  # Creates threads for both players which wait for
    t2 = threading.Thread(target=getattackposition, args=[playerconn2, 2])  # client to send attack location
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print "Game Over"
except Exception as e:
    print e.message
