import socket
import threading

connectionList = []  # keeps track of connection objects of clients
player1List = []  # contains ship positions of player 1
player2List = []  # contains ship positions of player 2


def establishconnection(serversocket):
    """
    waits for both players to get connected to server and sends responses to both clients when both are ready
    :param serversocket:
    :return:
    """
    conn, addr = serversocket.accept()
    connectionList.append(conn)
    conn, addr = serversocket.accept()
    connectionList.append(conn)
    sendready()


def sendready():
    """
    sends ready message to both clients so that they can proceed with further doings
    :return:
    """
    for i in connectionList:
        i.send("Ready")


try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates a server which listens to port 1234
    serversocket.bind(('0.0.0.0', 1234))    # 0.0.0.0 listens to all available interfaces
    serversocket.listen(0)
    establishconnection(serversocket)  # establishing connection to both clients
except Exception as e:
    print e.message
