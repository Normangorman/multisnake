from tkinter import *
from vectors import *
from gameboard import *
import json
import socket
import sys

MARGIN = 5
CELL_SIZE = 30
NUM_ROWS = 10
NUM_COLS = 10
WIDTH = CELL_SIZE * NUM_ROWS
HEIGHT = CELL_SIZE * NUM_COLS
DELAY = 250
GRID_LINE_COLOUR = "red"
SNAKE_DEFAULT_COLOUR = "purple"
SERVER_IP = "localhost"
SERVER_PORT = 9999

class Snake():
    def __init__(self, idNum, vecPos):
        self.idNum = idNum
        self.gridPos = vecPos
        self.direction = 0
        self.movementKeys = ['w','d','s','a']

    def getMovementRequest(self):
        request = {
            "idNum": self.idNum,
            "grid_x": self.gridPos.x,
            "grid_y": self.gridPos.y,
            "direction": self.direction
            }
        return request
    
    def receiveMovementResponse(self, response):
        if response.success == true:
            d = self.direction
            if d == 0:
                self.gridPos.y -= 1
            elif d == 1:
                self.gridPos.x += 1
            elif d == 2:
                self.gridPos.y += 1
            else:
                self.gridPos.x -= 1
        else:
            #TODO: Kill snake
            print("SNAKE DIED! idNum: " + str(self.idNum))

    # Queries the input manager to see if direction has been changed due to key press
    def update(self):
        for i in range(0,4):
            keyCode = self.movementKeys[i]
            if INPUT_MANAGER.wasKeyPressed(keyCode):
                self.direction = i

class SnakeClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        

    def sendSnakeDataGetResponse(self, snakeRequest):
        request_string = json.dumps(snakeRequest)
        print("SnakeClient.sendSnakeDataGetResponse: request_string = ", request_string)
            
        try:
            # Connect to server and send data
            # SOCK_STREAM means a TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.sendall(bytes(request_string + "\n", "utf-8"))

            # Receive data from the server and shut down
            response = sock.recv(1024).decode("utf-8")
        finally:
            sock.close()

        print("SnakeClient.sendSnakeDataGetResponse: response = ", response)
        return response


class InputManager():
    def __init__(self):
        self.keyPresses = []

    def handleKeyPress(self, event):
        self.keyPresses.append(event.char)
        print("A key was pressed: " + event.char)

    def wasKeyPressed(self, keyCode):
        return keyCode in self.keyPresses

    def clear(self):
        self.keyPresses = []

class GameManager():
    def __init__(self):
        self.renderScenery()
        self.localPlayer = Snake(1, Vector2(2, 2))
        self.snakes = []
        self.snakes.append(self.localPlayer)
        
        self.gameBoard = GameBoard(NUM_ROWS, NUM_COLS)
        self.snakeClient = SnakeClient(SERVER_IP, SERVER_PORT)

    def update(self):
        for snake in self.snakes:
            snake.update()
            self.gameBoard.markCell(snake.gridPos, snake.idNum)
            
        # Send local snake data to server and get info about the other snake movements.
        mv_req        = self.localPlayer.getMovementRequest()
        json_response = self.snakeClient.sendSnakeDataGetResponse(mv_req)
        response      = json.loads(json_response)

        print("GameManager.update: json_response = " + str(response))

        print("GameManager.update: response[\"success\"] = ", response["success"])
    
        
    def render(self):
        self.renderScenery()
        self.renderSnakes()

    def renderScenery(self):
        for i in range(1, NUM_COLS):
            x = CELL_SIZE * i
            CANVAS.create_line(x, 0, x, HEIGHT, fill=GRID_LINE_COLOUR)

        for i in range(1, NUM_ROWS):
            y = CELL_SIZE * i
            CANVAS.create_line(0, y, WIDTH, y, fill=GRID_LINE_COLOUR)

    def renderSnakes(self):
        for i in range(0, NUM_ROWS):
            for j in range(0, NUM_COLS):
                snakeIdNum = self.gameBoard.getCellData(Vector2(i,j))
                if snakeIdNum != 0: # the cell is not empty
                    self.renderSquare(Vector2(i,j))

    def renderSquare(self, vecPos):
        # + 1px so as to not coincide with grid lines
        xpos = vecPos.x * CELL_SIZE + 1
        ypos = vecPos.y * CELL_SIZE + 1
        width = CELL_SIZE - 2
        height = CELL_SIZE - 2
        
        CANVAS.create_rectangle(xpos, ypos,
                                xpos+width, ypos+height,
                                fill=SNAKE_DEFAULT_COLOUR)

MASTER = Tk()
CANVAS = Canvas(MASTER, width=WIDTH, height=HEIGHT)
CANVAS.pack()

INPUT_MANAGER = InputManager()
MASTER.bind_all('<Key>', INPUT_MANAGER.handleKeyPress)
GAME_MANAGER  = GameManager()

def gameLoop():
    print("Updating...")
    GAME_MANAGER.update()
    INPUT_MANAGER.clear()
    print("Rendering...")
    GAME_MANAGER.render()
    MASTER.after(DELAY, gameLoop)

MASTER.after(DELAY, gameLoop)
MASTER.mainloop()
