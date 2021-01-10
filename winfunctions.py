import win32gui as wgui #pip installed
import random
import math

#pip installed
from pynput.mouse import Button, Controller
mouse = Controller()

class win:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.gridSize = type('', (), dict(w=0,h=0))()
        self.gameOver = 0

        tup = wgui.GetWindowPlacement(self.hwnd)
        #PyHandle(dc), used for some wgui methods
        self.dc = wgui.GetWindowDC(self.hwnd)
        
        #get top left cell position, each cell position is calculated from this base
        self.x = tup[4][0]
        self.y = tup[4][1]
        self.w = tup[4][2]-tup[4][0]
        self.h = tup[4][3]-tup[4][1]
        self.topLeft = [self.x+23,self.y+108] #top left position is static to window position
        
        #old minesweeper has 3 are static window sizes
        if (self.w == 506) and (self.h == 368): #expert
            self.gridSize.w = 30
            self.gridSize.h = 16
        if (self.w == 282) and (self.h == 368): #intermediate
            self.gridSize.w = 16
            self.gridSize.h = 16
        if (self.w == 170) and (self.h == 256): #easy
            self.gridSize.w = 9
            self.gridSize.h = 9
        #creating gridData map
        gridData = []
        #for i in range(self.gridSize.h):
        i = 0
        while i < self.gridSize.w:
            i += 1
            column = []
            #for i in range(self.gridSize.w):
            ci = 0
            while ci < self.gridSize.h:
                ci += 1
                column.append("x") #innitial value "x" for unknown
                
            gridData.append(column)
        
        self.gridData = gridData

    def getRandom(self):
        """
        returns random empty cell
        """
        array = []
        xi = 0
        while (xi < self.gridSize.w):
            yi = 0
            while (yi < self.gridSize.h):
                if (self.gridData[xi][yi] == "x"):
                        array.append([xi,yi])
                yi += 1
            xi += 1
        return array[ random.randint(0, len(array)-1) ]

    def getNeighbour(self,x,y,target):
        """
        returns array of cells of target value[4th param] around target cell[x,y]
        maximum len(array)=8
        """
        AoO = getAreaAoO(x,y,1,self.gridSize.w,self.gridSize.h)
        
        array = []
        for i in range(len(AoO)):
            if (AoO[i].x == x) and (AoO[i].y == y):
                continue
            if (self.gridData[AoO[i].x][AoO[i].y] == target):   
                array.append( [AoO[i].x,AoO[i].y] )
        return array
            
    def checkWin(self,lastScan = 0):
        #check for win
        xi = 0
        while (xi < self.gridSize.w):
            yi = 0
            while (yi < self.gridSize.h):
                if (self.gridData[xi][yi] == "x"):
                    return 0
                yi += 1
            xi += 1
        if (lastScan == 0): #last large actual scan in case a cell was not marked via area scan and is not mapped, affects solve speed only in case of an error
            win.scanArea(self,self.gridSize.w/2,self.gridSize.h/2,self.gridSize.w/2)
            win.checkWin(self,1)

        return 1
    
    def restartGame(self):
        mouse.position = (self.x+self.w/2, self.y+70) #smiley position
        mouse.press(Button.left)
        mouse.release(Button.left)
    
    def click(self,x,y,m = 0):
        mouse.position = (self.topLeft[0]+x*16, self.topLeft[1]+y*16)
        if (m == 0):
            mouse.press(Button.left)
            mouse.release(Button.left)
        else: #use mark mines for visibility, error checking (turn on play function line 45)
            mouse.press(Button.right)
            mouse.release(Button.right)

    def scanArea(self,x,y,size):
        """
        updates gridData in given area
        submit x,y = position of center square
        size = 
        """
        areaScope = getAreaScope(x,y,size)
        #looping through scan area and updating gridData
        i = 0
        cy = math.floor(areaScope.tlY)
        while (i < areaScope.areaSize):
            ci = -1
            cx = math.floor(areaScope.tlX-1)
            while (ci < areaScope.areaSize):
                ci += 1
                cx += 1
                if (cx < 0) or (cy < 0) or (cx > self.gridSize.w-1) or (cy > self.gridSize.h-1):
                    continue
                if isinstance(self.gridData[cx][cy], int): #position has number already assigned
                    continue
                if (self.gridData[cx][cy] == "m"): #mine assigned to position
                    continue
                #scan position by getpixel method
                v = win.getSquare(self,cx,cy)
                if (v == -2): # out of grid
                    continue
                if (v == "x"): # innitial unknown value
                    continue
                if (v == -1): # mine detected
                    self.gameOver = 1
                    return self
                self.gridData[cx][cy] = v
            cy += 1
            i += 1  

        return self

    def getSquare(self,x,y):
        
        """
        submit: x & y of target cell
        returns:
        -1      -> mine found -> game over
        -2      -> submit out of range
        0       -> position solved - empty, grey cell
        x       -> position unknown, innitial position
        num 1-8 -> number found on position
        """

        if (x < 0) or (y < 0) or (x > self.gridSize.w-1) or (y > self.gridSize.h-1):
            return -2
        convX = self.topLeft[0]+x*16-self.x #16 is base distance in pixels between cells
        convY = self.topLeft[1]+y*16-self.y
        color = wgui.GetPixel(self.dc, convX, convY)

        if (color == 0):
            return -1
        if (color == 12632256): # middle pixel of "12632256" can be "solved", "not solved" or "7"
            if (wgui.GetPixel(self.dc, convX-7, convY) == 16777215): #white border indicates not solved
                return "x"
            if (wgui.GetPixel(self.dc, convX+1, convY) == 0): #7 is black
                return 7
            return 0

        if (color == 16711680):
            return 1
        if (color == 32768):
            return 2
        if (color == 255):
            return 3
        if (color == 8388608):
            return 4
        if (color == 128):
            return 5
        if (color == 8421376):
            return 6
        if (color == 8421504):
            return 8

def getAreaScope(x,y,size):
    """
    submit x and y position of center of return area
    size = number of cells from center to edge (size*2+1) e.g. size 2 would be 5x5 (areaSize=5)
    returns object with top left cell x and y pos (tlX,tlY) and areaSize
    """
    return type('', (), dict(tlX=x-size,tlY=y-size,areaSize=size*2+1))()

def getAreaAoO(x,y,size,gridW,gridH):
    """
    similar to getAreaScope, but returns array of objects of cell coordinates
    """
    areaScope = getAreaScope(x,y,size)
    #looping through scan area and updating gridData
    bx = math.floor(areaScope.tlX)
    by = math.floor(areaScope.tlY)
    bsize = math.floor(areaScope.areaSize)
    rArray = []
    cy = by
    while (cy < by+bsize):
        cx = bx
        while (cx < bx+bsize):
            if (cx < 0) or (cy < 0) or (cx > gridW-1) or (cy > gridH-1):
                cx += 1
                continue
            rArray.append(type('', (), dict(x=cx,y=cy))())
            cx += 1
        cy += 1
    return rArray