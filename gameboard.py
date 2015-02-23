class GameBoard():
    def __init__(self, boardHeight, boardWidth):
        self.boardHeight = boardHeight
        self.boardWidth  = boardWidth
        self.board = []
        for i in range (0, boardHeight):
            self.board.append([])
            for j in range(0, boardWidth):
                self.board[i].append(0)

    # mark the cell as occupied with the respective snake's id number
    def markCell(self, vecPos, idNum):
        self.board[vecPos.y][vecPos.x] = idNum

    def isCellOutOfBounds(self, vecPos):
        isTooSmall = vecPos.y < 0 or vecPos.x < 0
        isTooLarge = vecPos.y > self.boardHeight - 1 or vecPos.x > self.boardWidth - 1
        return isTooSmall or isTooLarge

    def getCellData(self, vecPos):
        if self.isCellOutOfBounds(vecPos):
            return 0
        else:
            return self.board[vecPos.y][vecPos.x]
