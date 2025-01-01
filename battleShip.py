import numpy as np
import pandas as pd

class Simulation():
    def __init__(self,player1Board, player2Board):
        self.players = [player1Board,player2Board]
        self.clock = 0
    

#Note - currently refabbing to make all these functions get called within other Board object methods
    def runBoardSetupSteps(self):
        print(self.players)
        for x in self.players:
            for key, value in x.ships.items():
                userCellInput = x.userBoatPosPrompt(key,value)
                endBoatPoint = x.specifyBoatOrientation(userCellInput,key,value)
                print(f"this is the end point being passed to applyBoatPosition {endBoatPoint}")
                x.applyBoatPosition(key,value,userCellInput,endBoatPoint, count = 0)


class Board:
    def __init__(self):
        self.emptySpot = 0
        self.shipSafe = 1
        self.shipHit = 2
        self.emptySpotHit = 3
        self.gameBoard = np.zeros((10,10))
        self.boardRows = list("JIHGFEDCBA")
        self.boardColumns = [f'{x}' for x in range(10)]
        #self.boardColumns = [x for x in range(10)]
        self.ships = {
        "Carrier":5,
        "Battle Ship":4,
        "Destroyer":3,
        "Submarine":3,
        "Patrol Boat":2
        }
        self.orientationOptions = {
            '1':[1,0],          
            '2':[0,1],
            '3':[-1,0],
            '4':[0,-1],
            '5':[0,0] 
        }
        self.storedPositions = {
        "Carrier":'',
        "Battle Ship":'',
        "Destroyer":'',
        "Submarine":'',
        "Patrol Boat":''
        }
    
#userBoatPosPrompt(boatLength) 
#       boatLength = int reprsenting how many cells long the boat is 
#       returns-> boatStartPoint; string of starting cell for boat position
#       Futur fixes: make is so that spaces in input can get interpretted correctly
    def userBoatPosPrompt(self,boat,boatLength):
        print("Please select location for boat placement (must be in format XY\n -where X is letter A-J\n -where Y is number 0-9")
        print("You will be guided to set direction of your boat - this will mean that all positions for the current boat will be in the direction you selected")
        boatStartPoint = str(input(f"Starting cell for {boat} (boat length {boatLength})")).upper()
        if not self.checkBoatPositionInput(boatStartPoint):
            boatStartPoint = self.userBoatPosPrompt(boat,boatLength)
        return boatStartPoint

#checkValidPosition has 3 goals:
#1)Check proper length of user input for a cell position (2 characters)
#2)Check that character at position 0 is a letter A-J
#3)Check that character at position 1 is a number 0-9
#   uInput -> string from userBoatposPrompt user input; will be checked that it is in proper formate (string)
#   returns -> continueSelection; boolean that determines if selection is good or if method must be reren to get function selection (boolean)
    def checkBoatPositionInput(self,uInput):
        inputCheck = list(uInput.upper())
        continueSelection = False
        print(inputCheck[0])
        if len(inputCheck) != 2:
            print("your input isn't in the correct 2 digit format, please try again")
        elif inputCheck[0] not in self.boardRows:
            print("Your first digit is not in the proper letter format for cell rows; please try again")
        elif inputCheck[1] not in self.boardColumns:
            print("your second digit reprsenting your column selection was incorrect; please try again")
        else:
            continueSelection = True 
        return continueSelection

#translateUserCell takes User Input and returns it as a tuple of (X,Y) coordinates
    def translateUserCell(self,uInput):
        return (self.boardRows.index(uInput[0]),int(uInput[1]))
        

#specifyBoatOrientation prompts user to give selection for how to lay their selected ship
#   selectedCell -> Cell that player has already input during game running for where the boat will originally be placed
#   boat -> name of the boat that is being placed (string)
#   boatlength -> length of the boat that is being placed (int)
    def specifyBoatOrientation(self, selectedCell, boat, boatLength):
        #print("Select the direction you will place your boat (if the boat is found to go over the edge of the board, you will be asked to redo the input)")
        orientationSelect = self.promptOrientationSelect(selectedCell)
        #print(f"\n\n This is your check to see why your option isn't being selected:\n user input {orientationSelect}\n type {type(orientationSelect)}\n \n \n") #testing user orientation input
        print(f"This is the user input for orientation that's going into the checkValidPosition Input AND checkBoatOrientation ===> {orientationSelect}")
        self.checkValidPositionInput(selectedCell,boat,boatLength,orientationSelect) 
        endCellCheck = self.checkBoatOrientation(selectedCell,boat,boatLength,orientationSelect)
        print(f"this is the position that is being DEFINITEVLY returned to the Simulation object ===> {endCellCheck}")
        return endCellCheck


    def promptOrientationSelect(self,selectedCell):
        orientationChoice = input(f"Cell Selection {selectedCell}\n"
            "1) Up from selected cell\n"
            "2) Right from selected cell\n"
            "3) Down from selected cell\n"
            "4) Left from selected cell\n"
            "5) Select a different Starting cell"
        )
        return orientationChoice

#checkBoatOrientation will check to see if the direction that the player has input is valid for a particular boat's orientation 
#   selectedCell - user input of starting cell for particular boat (string)
#   boatLength - length of boat being positioned (int)
#   uBoatOrientation - direction that boat will be positioned per user input (int)
#   return PosFinal -> tuple of X,Y coordinate showing end point of boat getting placed on playing grid
#   Notes - maybe worth exploring splitting up this method??? Kinda big and does a lot 
    def checkBoatOrientation(self,selectedCell,boat, boatLength,uBoatOrientation):
        adjBoatPos = self.translateUserCell(selectedCell)
        redoInput = False
        print(f"\n this is your check that the correct orientation vector is being applied to your boat direction - {self.orientationOptions[uBoatOrientation]}\n"
        f"orientation select - {uBoatOrientation}\n" f"boat position, XY format {adjBoatPos}\n")
        PosFinal = [self.orientationOptions[uBoatOrientation][0]*(boatLength-1)+adjBoatPos[0],self.orientationOptions[uBoatOrientation][1]*(boatLength-1)+adjBoatPos[1]]
        print(f"final playing position being captured in checkBoatOrientation ===> {PosFinal}\n\n")
        #This is a stupid loop; you're checking both dimensions of the array, even if the first one fails
        for x in PosFinal:
            if x < 0 or x > len(self.gameBoard)-1:
                redoInput = True
        if redoInput:
            print("It seems like the orientation you tried to specify for your boat is not valid as it doesn't lie in the playing field; \n"
            "please try again or consider selecting a new starting position for your boat")
            PosFinal = self.specifyBoatOrientation(selectedCell,boat,boatLength) #changing this to PosFinal = ... made the code actually work - still need to understand why that is 
        
        return PosFinal
            

#checkValidPositionInput will check the user's selection for orientation of their current boat; if the option isn't valid, it will prompt the user to give their position input again
#   selectedCell -> selectedCell is the user's starting boat position option
#   FUTURE WORK - have to check that user input is even a number; right now a string will cause an issue
    def checkValidPositionInput(self,selectedCell, boat, boatLength, uBoatOrientation):
        if uBoatOrientation not in self.orientationOptions or len(uBoatOrientation) != 1:
            print("The input you have given for a boat orientation is not a valid option; please try again")
            self.specifyBoatOrientation(selectedCell, boat, boatLength)
        elif uBoatOrientation == '5': #this is uber stupid; need a cleaner way to call out the option was selected to repick the start cell. Just seeing a '5' is clean
            print("you've selected to repick your boat's starting position; please see below prompt to choose boat's position")
            uCell = self.userBoatPosPrompt(boat,boatLength)


#applyBoatPosition places the boats on the playing board as specified by the player starting cell and the range of cells specified by user input for boat orientation
    def applyBoatPosition(self,boat,boatLength,uCell,endCell,count):
        adjBoatPos = self.translateUserCell(uCell)
        if adjBoatPos[count] != endCell[count]:
            boardCoord = [x for x in adjBoatPos] 
            allBoatCoords = self.getBoatCoords(boardCoord,adjBoatPos,endCell,count)
            self.checkIntersection(boat,boatLength,allBoatCoords)
            for x in allBoatCoords:
                self.gameBoard[tuple(x)] = 1
        else:
            count += 1 
            self.applyBoatPosition(boat,boatLength,uCell,endCell,count)

#getBoatCoords returns a LIST of all the points that will be placed on the game board as part of a single boat 
    def getBoatCoords(self,boatCoord,adjBoatPos,endCell,count):
        allBoatCoords = []
        direction = self.findBoatDirection(adjBoatPos[count],endCell[count])
        for x in range(adjBoatPos[count],endCell[count]+direction,direction):
            boatCoord[count] = x
            allBoatCoords.append(boatCoord[:])
            print(allBoatCoords)
        return allBoatCoords
    
#findBoatDirection takes a certain axis of the game board from the start/end cells and checks to see how the boat will be placed (in descending/ascending order)
#   uCellDim - starting cell dimension input by user (int)
#   endCellDim - ending cell dimension input by user (int)
#   return direction - gives positive direction (+1) or negative direction (-1) that will dictate how the boat gets placed on the board (int)
    def findBoatDirection(self,uCellDim,endCellDim):
        if endCellDim >= uCellDim:
            direction = 1
        else:
            direction = -1
        return direction

#checkIntersection will send you back to the point where you'll need to put in a new selected position for your boat 
    def checkIntersection(self, boat, boatLength, potentialCoords):
        for x in potentialCoords:
            if self.gameBoard[tuple(x)] == 1: 
                uCell = self.userBoatPosPrompt(boat,boatLength)
                endCell = self.specifyBoatOrientation(uCell,boat,boatLength)
                self.intersectMessage()
                self.applyBoatPosition(boat,boatLength,uCell,endCell)
    

    def intersectMessage():
        print("It seems like you've placed a boat such that it overlaps with an existing boat on the board; please start again and try picking a new position for this current boat:")
                
                


myBoard1 = Board()
myBoard2 = Board()

testGame = Simulation(myBoard1,myBoard2)
testGame.runBoardSetupSteps()


#To do:
#   - build in functionality during ship position application to re-pick the cell position if desired 
#   - current user input filtering will flag if a user puts a space between characters selected; might be worth having a method that allows spaces 
#   - test intersection detecting capabilities 