import socketserver
from vectors import *
from gameboard import *
import json

class SnakeGame():
    def __init__(self, numPlayers, boardWidth, boardHeight):
        self.numPlayers = numPlayers
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight
        self.gameBoard = GameBoard(boardWidth, boardHeight)

        self.receivedMoves = []
        self.numMovesReceived = 0

    def receiveMoveRequestObject(self, moveRequestObject):
        self.numMovesReceived += 1
        return

    def getResponseObject(self):
        self.numMovesReceived = 0 # reset in preparation for next turn
        return '{"idNum": 10, "success": true}'

GAME = SnakeGame(1, 10, 10)

class SnakeServer(socketserver.BaseRequestHandler):
    """
    This is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = json.loads(self.request.recv(1024).decode('utf-8').strip())
        print("{} wrote:".format(self.client_address[0]))
        print(str(data))

        GAME.receiveMoveRequestObject(data)
        print("Number of moves received: ", GAME.numMovesReceived)

        if GAME.numMovesReceived == GAME.numPlayers:
            responseObject = GAME.getResponseObject()
            print("Received moves from all players.")
            print("Sending response: ", str(responseObject))
            
            response = bytes( json.dumps(responseObject), 'UTF-8' )
            self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), SnakeServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Number of players: ", GAME.numPlayers)
    print("Board Width: ", GAME.boardWidth)
    print("Board Height: ", GAME.boardHeight)
    print("Listening on port " + str(PORT) + "...")
    server.serve_forever()
