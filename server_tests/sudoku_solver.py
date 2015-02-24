import time
startingTime = time.clock()

grid = [
    [3,0,2, 0,0,0,  7,0,0],
    [0,0,0, 0,4,9,  0,1,8],
    [0,1,0, 0,7,0,  0,0,3],
    
    [0,5,0, 0,0,2,  0,0,0],
    [0,8,0, 0,1,0,  0,6,0],
    [0,0,0, 7,0,0,  0,4,0],
    
    [2,0,0, 0,5,0,  0,7,0],
    [1,7,9, 6,3,0,  0,0,0],
    [0,0,9, 0,0,0,  4,0,6]
    ]

def gridCol(n,g):
    col = []
    for row in g:
        col.append(row[n])
    return col
        
def gridRow(n,g):
    return g[n]
    
def gridBox(a,b,g):
    # Round to the nearest 3
    a = (a // 3) * 3
    b = (b // 3) * 3
    
    row1 = [gridRow(b,g)[a],      gridRow(b,g)[a+1],    gridRow(b,g)[a+2]]
    row2 = [gridRow(b+1,g)[a],    gridRow(b+1,g)[a+1],  gridRow(b+1,g)[a+2]]
    row3 = [gridRow(b+2,g)[a],    gridRow(b+2,g)[a+1],  gridRow(b+2,g)[a+2]]
    return row1 + row2 + row3


def getContext(x,y,g):
    cellCol = gridCol(x,g)
    cellRow = gridRow(y,g)
    cellBox = gridBox(x,y,g)
    return [cellCol, cellRow, cellBox]

def potentialValues (x,y,g):
    pots = []
    context = getContext(x,y,g)
    
    for n in range (1,10):
        if not ((n in context[0]) or (n in context[1]) or (n in context[2])):
            pots.append(n)
            continue
    return pots

def getPotentialValuesGrid(g):
    potValuesGrid = []
    for y in range (0,9):
        potsRow = []
        for x in range(0,9):
            if g[y][x] != 0:
                cellPots = []
            else:
                cellPots = potentialValues(x, y,g)
                
            potsRow.append(cellPots)
            
        potValuesGrid.append(potsRow)
    return potValuesGrid

def updateGrid(g):
    for y in range (0,9):
        for x in range(0,9):
            updateCell(x,y,g)
    return g

def concat(xs):
    ys = []
    for x in xs:
        ys += x
    return ys

def updateCell(x,y,g):
    potGrid         = getPotentialValuesGrid(g) 
    cellPots        = potGrid[y][x]
    contextPotRow   = concat(gridRow(y,potGrid))
    contextPotCol   = concat(gridCol(x,potGrid))
    contextPotGrid  = concat(gridBox(x,y,potGrid))

    value = 0
    if      len(cellPots) == 1:
        value = cellPots[0]
        print ("set (" + str(x) + ", " + str(y) + ") to: " + str(value) + " because it has only one potential value.")
        
    else:
        for n in cellPots:
            if contextPotRow.count(n) == 1:
                value = n
                print ("set (" + str(x+1) + ", " + str(y+1) + ") to: " + str(value) + " because no other cell in its row can have this value.")
                print (str(contextPotRow))
            elif contextPotCol.count(n) == 1:
                value = n
                print ("set (" + str(x+1) + ", " + str(y+1) + ") to: " + str(value) + " because no other cell in its column can have this value.")

            elif contextPotGrid.count(n) == 1:
                value = n
                print ("set (" + str(x+1) + ", " + str(y+1) + ") to: " + str(value) + " because no other cell in its box can have this value.")

    if value != 0:
        g[y][x] = value
        print 

def prettify(g):
    for row in g:
        print (str(row))
        
def complete(g):
    return not (0 in concat(g))

def solve():
    while (not complete(grid)) and (time.clock() - startingTime < 3):
        updateGrid(grid)

print (concat([[1,2],[3,4],[5,6,7]]))
print ()
prettify(grid)
prettify(getPotentialValuesGrid(grid))
solve()
prettify(grid)
runningTime = round(time.clock() - startingTime, 3)
print ()
print ("Puzzle solved in: " + str(runningTime) + " seconds.")

