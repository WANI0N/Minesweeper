#external lib
import sys
import win32gui as wgui
import time

#custom lib
from winfunctions import win

#retreive hwnd of target window
hwnd = wgui.FindWindow("Minesweeper",None)

#verify successful hwnd retreival
try:
    wgui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
except:
    print("Minesweeper window not found")
    sys.exit()

def play(self,random = 0):
    #verify game over or win
    if (self.gameOver == 1):
        return False
    if (win.checkWin(self) == 1):
        return True
    #move random empty cell if submitted
    if (random == 1):
        randomMove = win.getRandom(self)
        win.click(self,randomMove[0],randomMove[1])
        self = win.scanArea(self,randomMove[0],randomMove[1],4)
        play(self)
    
    #find number cell and mark mines, then click neighbours
    xi = 0
    progress = 0
    while (xi < self.gridSize.w):
        yi = 0
        while (yi < self.gridSize.h):
            if isinstance(self.gridData[xi][yi], int) and (self.gridData[xi][yi] != 0):
                unknown = win.getNeighbour(self,xi,yi,"x") #retrieve array of unknown (x) cells from 8 possible cell neighbours
                mines = win.getNeighbour(self,xi,yi,"m") #same for mines
                if (len(unknown)+len(mines) == self.gridData[xi][yi]): #if number of mines+unknown equals target cell number
                    for cell in unknown: #mark mines
                        self.gridData[ cell[0] ] [ cell[1] ] = "m"
                        #win.click(self,cell[0],cell[1],1) #mark mines for debugging, else disable for speed boost
                
                # repeat neighbour scan for updated info from mine marking
                unknown = win.getNeighbour(self,xi,yi,"x")
                mines = win.getNeighbour(self,xi,yi,"m")
                scan = 0
                # if mines = target number, reveal remaining unkonw neighbours
                if (len(mines) == self.gridData[xi][yi]):
                    for cell in unknown:
                        win.click(self,cell[0],cell[1])
                        if (self.gameOver == 1):
                            return False                        
                        scan = 1
                if (scan == 1): #scan area (actually via getPixel if valid scan (or click has been made))
                    progress = 1 #mark progress
                    self = win.scanArea(self,xi,yi,5)
            yi += 1
        xi += 1
    #if progress made, repeat, else move random
    if (progress == 0):
        return play(self,1)
    return play(self)

#repeat play until r=True ~win
r = False
while (r == False):
    winData = win(hwnd) #innitiate winData object; retreive coordinates of target window, creates map (winData.GridData), declares top left cell position
    win.restartGame(winData) #start new game
    time.sleep(0.1) #allow window to respond
    r = play(winData,1) #innitiate play with random move
    print(r)
    time.sleep(1) #allow 1 sec to cancel process in terminal via CTRL+C

