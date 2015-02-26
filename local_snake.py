from tkinter import *
from tkinter.colorchooser import *
from vectors import *
import json
import sys
import math
import time

MARGIN = 5
CELL_SIZE = 22
NUM_ROWS = 30
NUM_COLS = 30
WIDTH = CELL_SIZE * NUM_ROWS
HEIGHT = CELL_SIZE * NUM_COLS
DELAY = 50
SNAKE_DEFAULT_COLOUR = "#FF3300"
SERVER_IP = "localhost"
SERVER_PORT = 9999
SOLID_WALLS = True
GRID_BACKGROUND_COLOUR_1 = "#000066"
GRID_BACKGROUND_COLOUR_2 = "#191975"
GRID_LINE_COLOUR = "#4D4D94"
WINDOW_TITLE = "Cobra"
DEFAULT_FONT = ("Arial", "12")

class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)

    def toString(self):
        return "x: {0}, y: {1}".format(self.x, self.y)
    
class Snake():
    def __init__(self, idNum, startPos, name, colour=SNAKE_DEFAULT_COLOUR, movementKeys=['w','d','s','a']):
        self.idNum = idNum
        self.startPos = startPos
        self.gridPos = Vector2(startPos.x, startPos.y)
        self.name = name
        self.direction = 0
        self.movementKeys = movementKeys
        self.alive = True
        self.colour = colour
        self.trail = [startPos]
        self.score = 0
        self.ready = False

    def reset(self):
        #fixes bug where gridPos and startPos refer to the same memory location
        self.gridPos = Vector2(self.startPos.x, self.startPos.y)
        self.direction = 0
        self.alive = True
        self.trail = [self.startPos]
        self.ready = False

    # Queries the input manager to see if direction has been changed due to key press
    def update(self, inputManager):
        self.trail.append(self.gridPos)
        if self.alive:
            d = self.direction
            for i in range(0,4):
                keySym = self.movementKeys[i]

                # Prevent the snake from turning back on itself
                turnedBack = sorted([i,d]) == [0,2] or sorted([i,d]) == [1,3]
                if inputManager.wasKeyPressed(keySym) and not turnedBack:
                    self.direction = i

            if d == 0:
                self.gridPos.y -= 1
            elif d == 1:
                self.gridPos.x += 1
            elif d == 2:
                self.gridPos.y += 1
            else:
                self.gridPos.x -= 1

    def changePosModuloGridSize(self, gridWidth, gridHeight):
        self.gridPos.x %= gridWidth
        self.gridPos.y %= gridHeight

    def isReady(self, inputManager):
        if self.ready:
            return True

        for i in range(0, 4):
            if inputManager.wasKeyPressed(self.movementKeys[i]):
                self.direction = i
                self.ready = True
                print("Snake {0} is ready.".format(str(self.idNum)))

        return self.ready

    def die(self):
        print("Snake with id {0} died!".format(self.idNum))
        self.alive = False
        return
       

class GameBoard():
    def __init__(self, boardHeight, boardWidth):
        self.boardHeight = boardHeight
        self.boardWidth  = boardWidth
        self.board = []
        for i in range (0, boardHeight):
            self.board.append([])
            for j in range(0, boardWidth):
                self.board[i].append(0)

    def reset(self):
        for i in range (0, self.boardHeight):
            for j in range(0, self.boardWidth):
                self.board[i][j] = 0

    # mark the cell as occupied with the respective snake's id number
    def markCell(self, vecPos, idNum):
        self.board[vecPos.y][vecPos.x] = idNum

    def _isCellOutOfBounds(self, vecPos):
        isTooSmall = vecPos.y < 0 or vecPos.x < 0
        isTooLarge = vecPos.y > self.boardHeight - 1 or vecPos.x > self.boardWidth - 1
        return isTooSmall or isTooLarge

    def getCellData(self, vecPos):
        # cellData is -1 for out of bounds, 0 for empty or something > 0 for occupied
        if self._isCellOutOfBounds(vecPos):
            return -1
        else:
            return self.board[vecPos.y][vecPos.x]

    def didSnakeHitSomething(self, snake):
        data = self.getCellData(snake.gridPos)
        if data == 0:
            return False
        else:
            return True

class InputManager():
    def __init__(self):
        self.keyPresses = []

    def handleKeyPress(self, event):
        self.keyPresses.append(event.keysym)
        print("A key was pressed: " + event.keysym)

    def wasKeyPressed(self, keySym):
        return keySym in self.keyPresses

    def clear(self):
        self.keyPresses = []

class UIManager():
    def __init__(self, master):
        self.master = master
        self.widgets = {}
        self.defaultFont = ("Arial", "12")

    def setupGame(self, snakes):
        headings = ["Name", "Colour", "Score"]
        numRowsUsed = 0
        for i in range(0, len(headings)):
            w = Label(self.master, font=("Arial","12", "bold"), justify="center", text=headings[i])
            w.grid(row=0, column=i)

        numRowsUsed += 1

        self.widgets["snakeInfo"] = {}
        for snake in snakes:
            snakeWidgets = {}
            name = Label(self.master, font=self.defaultFont, justify="center", text=snake.name)
            name.grid(row=numRowsUsed, column=0)
            snakeWidgets["name"] = name

            colour = Canvas(self.master, width=30, height=30)
            colour.create_rectangle(0,0,30,30,fill=snake.colour)
            colour.grid(row=numRowsUsed, column=1)
            snakeWidgets["colour"] = colour

            score = Label(self.master, font=self.defaultFont, justify="center", text=str(snake.score))
            score.grid(row=numRowsUsed, column=2)
            snakeWidgets["score"] = score

            self.widgets["snakeInfo"][snake.name] = snakeWidgets

            numRowsUsed += 1

        statusLine = Label(self.master, font=self.defaultFont, justify="center", text="")
        statusLine.grid(row=numRowsUsed, column=0, columnspan=3, pady=5)
        numRowsUsed += 1
        self.statusLine = statusLine

        canvas = Canvas(self.master, width=WIDTH, height=HEIGHT, borderwidth=2, relief="raised")
        canvas.grid(row=numRowsUsed, column=0, columnspan=3, pady=10, padx=10)
        self.canvas = canvas

    def updateSnakeScores(self, snakes):
        print("Updating snake scores.")
        for snake in snakes:
            print("Score: " + str(snake.score))
            self.widgets["snakeInfo"][snake.name]["score"]["text"] = str(snake.score)

        self.master.update_idletasks()

    def setStatusLine(self, msg):
        self.statusLine["text"] = msg

    def renderSnakes(self, snakes):
        for snake in snakes:
            if len(snake.trail) > 0:
                snakeHeadPosition = snake.trail[-1]
                self.renderSquare(snakeHeadPosition, snake.colour)

    def renderSquare(self, vecPos, colour=SNAKE_DEFAULT_COLOUR):
        # + 1px so as to not coincide with grid lines
        xpos = vecPos.x * CELL_SIZE + 5
        ypos = vecPos.y * CELL_SIZE + 5
        width = CELL_SIZE - 2
        height = CELL_SIZE - 2
        
        self.canvas.create_rectangle(xpos, ypos,
                                xpos+width, ypos+height,
                                fill=colour)

    def renderRoundOverBox(self, text):
        mid_xpos = WIDTH / 2
        mid_ypos = HEIGHT / 2
        box_width = min(200, WIDTH)
        padding = 10
        
        self.canvas.create_rectangle(mid_xpos - box_width/2, mid_ypos-75,
                                mid_xpos + box_width/2, mid_ypos+75,
                                fill="peach puff")
        self.canvas.create_text((mid_xpos, mid_ypos),
                           text=text,
                           font=("Arial", "24"),
                           justify="center",
                           width=box_width - 2*padding)

    def renderGameOverBox(self, text):
        mid_xpos = WIDTH / 2
        mid_ypos = HEIGHT / 2
        box_width = min(300, WIDTH)
        padding = 10
        
        self.canvas.create_rectangle(mid_xpos - box_width/2, mid_ypos-125,
                                mid_xpos + box_width/2, mid_ypos+125,
                                fill="peach puff")
        self.canvas.create_text((mid_xpos, mid_ypos),
                           text=text,
                           font=("Arial", "24"),
                           justify="center",
                           width=box_width - 2*padding)

    def renderScenery(self):
        for i in range(1, NUM_COLS):
            x = CELL_SIZE * i + 4
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID_LINE_COLOUR)

        for i in range(1, NUM_ROWS):
            y = CELL_SIZE * i + 4
            self.canvas.create_line(0, y, WIDTH, y, fill=GRID_LINE_COLOUR)

        # Fill in the alternating cell background pattern
        colourNum = 1
        for i in range(0, NUM_ROWS):
            for j in range(0, NUM_COLS):
                if colourNum == 1:
                    colour = GRID_BACKGROUND_COLOUR_1
                    colourNum = 2
                else:
                    colour = GRID_BACKGROUND_COLOUR_2
                    colourNum = 1
                vec = Vector2(j,i)
                self.renderSquare(vec, colour)

            if NUM_COLS % 2 == 0:
                if colourNum == 2: colourNum = 1
                else: colourNum = 2


class GameManager():
    def __init__(self, maxScore=3):
        self.numPlayers = 0
        self.playerData = []
        self.snakes = []
        self.gameBoard = GameBoard(NUM_ROWS, NUM_COLS)
        self.roundFinished = False
        self.numDeadSnakes = 0
        self.maxScore = maxScore
        self.roundJustFinished = False
        self.gameOver = False
        self.allSnakesReady = False
        self.paused = False
        self.pauseTime = 0
        self.UIManager = None #set in start
        self.InputManager = None # set in start

    def start(self, snakeData):        
        self.UIManager = UIManager(MASTER)
        self.InputManager = InputManager()
        MASTER.bind_all('<Key>', self.InputManager.handleKeyPress) # THIS COULD CAUSE A BUG IF TRYING TO PLAY A SECOND GAME
        self.numPlayers = len(snakeData)

        # Given n players, construct a n-sided regular polygon and use the vertices to decide on snake starting points.
        middlePoint = Vector2( round(NUM_COLS/2), round(NUM_ROWS/2) )
        radius = ((NUM_COLS/2) * 0.6 + (NUM_ROWS/2) * 0.6) / 2
        theta = 2*math.pi / self.numPlayers
        startPoints = []
        for i in range(0, self.numPlayers):
            x = radius * math.cos(theta * i)
            y = radius * math.sin(theta * i)
            point = Vector2.add(middlePoint, Vector2(round(x), round(y)))
            startPoints.append(point)

        # Create snake objects and add them to players list, using the starting points just created.
        for i in range(1, self.numPlayers + 1):
            snake_idNum = i
            snake_startPoint = startPoints[i-1]
            snake_colour = snakeData[i-1]["colour"]
            snake_keys = snakeData[i-1]["movementKeys"]
            snake_name = snakeData[i-1]["name"]
            if snake_name == "":
                snake_name = "Player " + str(snake_idNum)

            s = Snake(snake_idNum, snake_startPoint, snake_name, colour=snake_colour, movementKeys=snake_keys)
            self.snakes.append(s)
            print("Snake made. idNum: {0}, name: {1}".format(snake_idNum, snake_name))

        self.UIManager.setupGame(self.snakes)
        self.UIManager.renderScenery()

    def endRound(self):
        # checked in render method to prevent render immediately after the round-ending update
        self.roundJustFinished = True 
        if self.numDeadSnakes == self.numPlayers: #multiple snakes died simultaneously so it's a draw
            self.UIManager.renderRoundOverBox("It's a draw!")
        else:
            for snake in self.snakes:
                if snake.alive:
                    winning_snake = snake
                    winning_snake.score += 1
                    if winning_snake.score == self.maxScore:
                        self.endGame(winning_snake)
                        return

            self.UIManager.renderRoundOverBox("{0} wins the round.".format(winning_snake.name))

        for snake in self.snakes:
            snake.reset()

        self.gameBoard.reset()
        self.numDeadSnakes = 0
        self.allSnakesReady = False
        self.UIManager.updateSnakeScores(self.snakes)
        self.pause(1000)
        print("New round started.")

    def endGame(self, winningSnake):
        print("Game ending.")
        self.roundJustFinished = True 
        self.gameOver = True

        secondHighestScore = 0
        for snake in self.snakes:
            if snake != winningSnake and snake.score > secondHighestScore:
                secondHighestScore = snake.score

        scoreDelta = winningSnake.score - secondHighestScore
        if scoreDelta > round(self.maxScore * 0.5):
            victoryMessage = "{0} demolishes the opposition!".format(winningSnake.name)
        elif scoreDelta > round(self.maxScore * 0.25):
            victoryMessage = "A sound victory by {0}.".format(winningSnake.name)
        else:
            victoryMessage = "{0} wins. A close game!".format(winningSnake.name)

        self.UIManager.updateSnakeScores(self.snakes)
        self.UIManager.renderGameOverBox("Game over. " + victoryMessage)
        MASTER.unbind('<Key>') # unbind from input_manager
        self.pause(5000)

    def pause(self, duration):
        self.paused = True
        self.pauseTime = duration

    def getSnakeById(self, idNum):
        return self.snakes[idNum-1]

    def update(self): 
        if self.numDeadSnakes >= self.numPlayers - 1:
            self.endRound()
            return
            
        if not self.allSnakesReady:
            numReadySnakes = 0
            for snake in self.snakes:
                if snake.isReady(self.InputManager):
                    numReadySnakes += 1
                else:
                    idleSnake = snake

            if numReadySnakes == self.numPlayers:
                self.allSnakesReady = True
                self.UIManager.setStatusLine("Round started.")
            else:
                numSnakesToGo = self.numPlayers - numReadySnakes
                if numSnakesToGo == 1:
                    self.UIManager.setStatusLine("Still waiting for {0} to be ready. Come on!".format(idleSnake.name))
                else:
                    self.UIManager.setStatusLine("Still waiting for {0} players to be ready.".format(numSnakesToGo))

        else:
            for snake in self.snakes:
                if snake.alive:
                    snake.update(self.InputManager)

                    cellData = self.gameBoard.getCellData(snake.gridPos)
                    if cellData == -1: #the snake hit a wall
                        if SOLID_WALLS:
                            snake.die()
                            self.numDeadSnakes += 1
                        else:
                            snake.changePosModuloGridSize(NUM_COLS, NUM_ROWS)
                            self.gameBoard.markCell(snake.gridPos, snake.idNum)
                    elif cellData == 0: #the snake is fine
                        self.gameBoard.markCell(snake.gridPos, snake.idNum)
                    else: # the snake hit an occupied cell
                        snake.die()
                        self.numDeadSnakes += 1
        
    def render(self):
        if self.gameOver:
            return
        elif self.roundJustFinished and not self.paused:
            self.roundJustFinished = False
            self.UIManager.renderScenery()
        else:
            self.UIManager.renderSnakes(self.snakes)

    def loop(self):
        print("Game looping.")
        if self.gameOver:
            # Restart main menu
            for child in MASTER.winfo_children():
                child.grid_forget()
            m = MainMenu(MASTER)
            m.start()
            print("Starting main menu.")
            return
            
        else:
            self.update()
            self.render()

        if self.paused:
            MASTER.after(DELAY + self.pauseTime, self.loop)
            self.paused = False
            self.pauseTime = 0
        else:
            MASTER.after(DELAY, self.loop)
        self.InputManager.clear()

class MainMenu():
    class PlayerEntryRow():
        def __init__(self, master, rowNum):
            self.deleted = False
            self.colourPickerColour = SNAKE_DEFAULT_COLOUR
            self.rowNum = rowNum
            self.name = ""
            self.colour = SNAKE_DEFAULT_COLOUR
            self.movementKeys = ['w','d','s','a']
            
            nameEntry = Entry(master, font=("Arial", "12"), justify="center")
            nameEntry.grid(row=rowNum, column=0)
            self.nameEntry = nameEntry

            colourPicker = Canvas(master, width=30, height=30)
            colourPicker.create_rectangle(0,0,30,30,fill=SNAKE_DEFAULT_COLOUR)
            colourPicker.grid(row=rowNum, column=1)
            colourPicker.bind("<Button-1>", self.editColour)
            self.colourPicker = colourPicker

            movementOptions = [
                "WASD",
                "YGHJ",
                "PL;'",
                "Arrow keys"
            ]
            defaultOption = StringVar(master)
            defaultOption.set(movementOptions[0])
            movementKeysPicker = OptionMenu(master, defaultOption, *tuple(movementOptions))
            movementKeysPicker.grid(row=rowNum, column=2)
            self.movementKeysPicker = movementKeysPicker

            if rowNum > 2:
                # There must be a minimum of two players so don't allow the user to delete the 1st or 2nd player
                deleteButton = Button(master, font=DEFAULT_FONT, justify="center", text="Delete", command=self.delete)
                deleteButton.grid(row=rowNum, column=3)
                self.deleteButton = deleteButton

        def editColour(self, event):
            (rgbVals, colourString) = askcolor()
            self.colourPicker.create_rectangle(0,0,30,30,fill=colourString)
            self.colourPickerColour = colourString
            print("Edit colour: " + colourString)

        def getPlayerData(self):
            name = self.nameEntry.get()
            colour = self.colourPickerColour
            keys = self.movementKeysPicker["text"]
            if keys == "WASD":
                print("Keys: WASD")
                keys = ['w','d','s','a']
            elif keys == "YGHJ":
                print("Keys: YGHJ")
                keys = ['y','j','h','g']
            elif keys == "PL;'":
                print("Keys: PL;'")
                keys = ['p', "'", ';', 'l']
            elif keys == "Arrow keys":
                print("Keys: Arrow keys")
                keys = ['Up', 'Right', 'Down', 'Left']
            else:
                print("getPlayerData(): movementKeysPicker value not recognized! - " + keys)

            return {"name": name, "colour": colour, "movementKeys": keys}

        def delete(self):
            self.deleted = True
            # Delete all the widgets
            self.nameEntry.grid_forget()
            self.colourPicker.grid_forget()
            self.movementKeysPicker.grid_forget()
            self.deleteButton.grid_forget()

        #END OF PlayerEntryRow

    def __init__(self, master):
        self.master = master
        self.defaultFont = ("Arial", "12")
        self.numRowsUsed = 0
        self.ready = False
        self.playerEntryFrame = None # set in start method
        self.playerEntryRows = []

    def start(self):
        print("Started main menu")
        # Main title
        title = Label(self.master, font=("Arial", "16", "bold"), justify="center", text="Cobra", padx=15, pady=15)
        title.grid(row=0, column=0, columnspan=3)
        self.numRowsUsed += 1
        
        # Buttons
        buttonFrame = Frame(width=WIDTH)
        buttonFrame.grid(row=self.numRowsUsed, columnspan=3)
        # Add new player button
        newPlayerButton = Button(buttonFrame, text="Add a player", command=self.addPlayerEntryRow)
        newPlayerButton.grid(row=self.numRowsUsed, column=0)
        # Play button
        playButton = Button(buttonFrame, text="Play!", command=self.play)
        playButton.grid(row=self.numRowsUsed, column=1)
        # Quit button
        quitButton = Button(buttonFrame, text="Quit :(", command=self.quit)
        quitButton.grid(row=self.numRowsUsed, column=2)
        self.numRowsUsed += 1

        # Player entry frame
        self.playerEntryFrame = Frame()
        self.playerEntryFrame.grid(row=self.numRowsUsed)
        self.numRowsUsed += 1
        
        # Column headings
        headings = ["Name", "Colour", "Movement keys"]
        for i in range(0, len(headings)):
            w = Label(self.playerEntryFrame, font=("Arial","12", "bold"), justify="center", text=headings[i])
            w.grid(row=0, column=i)

        # Should be a minimum of 2 players
        self.addPlayerEntryRow()
        self.addPlayerEntryRow()
        print("Finished creating menu widgets")

    def addPlayerEntryRow(self):
        row = self.PlayerEntryRow( self.playerEntryFrame, len(self.playerEntryRows)+1 ) #+1 due to labels row
        self.playerEntryRows.append(row) 
        
    def quit(self):
        self.master.destroy()
        sys.exit()

    def play(self):
        print("Playing game")
        for child in MASTER.winfo_children():
            child.grid_forget()
            
        playerData = []
        for row in self.playerEntryRows:
            if not row.deleted:
                playerData.append(row.getPlayerData())

        print("Player data: " + str(playerData))
        gm = GameManager(maxScore=5)
        gm.start(playerData)
        gm.loop()

MASTER = Tk()
MASTER.wm_title(WINDOW_TITLE)
MASTER.resizable(width=False, height=False)

MAIN_MENU = MainMenu(MASTER)
MAIN_MENU.start()

MASTER.mainloop()
