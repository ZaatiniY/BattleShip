import numpy as np
import pandas as pd

class Simulation():
    def __init__(self,player1Board, player2Board):
        self.players = [player1Board,player2Board]
        self.clock = 0
    
    def runBoardSetupSteps(self):
        print(self.players)
        for x in self.players:
            for key, value in x.ships.items():
                userCellInput = x.userBoatPosPrompt(key,value)
                x.specifyBoatOrientation(userCellInput,key,value)

                

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
            '1':[0,1],          
            '2':[1,0],
            '3':[0,-1],
            '4':[-1,0],
            '5':[0,0] 
        }
    
#userBoatPosPrompt(boatLength) 
#       boatLength = int reprsenting how many cells long the boat is 
#       returns-> boatStartPoint; string of starting cell for boat position
#       Futur fixes: make is so that spaces in input can get interpretted correctly
    def userBoatPosPrompt(self,key,value):
        print("Please select location for boat placement (must be in format XY\n -where X is letter A-J\n -where Y is number 0-9")
        print("You will be guided to set direction of your boat - this will mean that all positions for the current boat will be in the direction you selected")
        boatStartPoint = str(input(f"Starting cell for {key} (boat length {value})"))
        userCheck = self.checkBoatPositionInput(boatStartPoint)
        if userCheck:
            return boatStartPoint 
        else:
            self.userBoatPosPrompt(key,value)

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

#translateUserCell takes User Input and returns it as a tuple of (X,Y coordinates1)
    def translateUserCell(self,uInput):
        return (self.boardRows.index(uInput[0]),int(uInput[1]))
        

#specifyBoatOrientation prompts user to give selection for how to lay their selected ship
#   selectedCell -> Cell that player has already input during game running for where the boat will originally be placed
#   boat -> name of the boat that is being placed (string)
#   boatlength -> length of the boat that is being placed (int)
    def specifyBoatOrientation(self,selectedCell, boat, boatLength):
        print("Select the direction you will place your boat (if the boat is found to go over the edge of the board, you will be asked to redo the input)")
        orientationSelect = input(f"Cell Selection {selectedCell}\n"
            "1) Up from selected cell\n"
            "2) Right from selected cell\n"
            "3) Down from selected cell\n"
            "4) Left from selected cell\n"
            "5) Select a different Starting cell"
        )
        print(f"\n\n This is your check to see why your option isn't being selected:\n user input {orientationSelect}\n type {type(orientationSelect)}\n \n \n")
        self.checkValidPositionInput(selectedCell,boat,boatLength,orientationSelect) 
        boatPosEnd = self.checkBoatOrientation(selectedCell,boat,boatLength,orientationSelect)

#checkBoatOrientation will check to see if the direction that the player has input is valid for a particular boat's orientation 
#   selectedCell - user input of starting cell for particular boat (string)
#   boatLength - length of boat being positioned (int)
#   uBoatOrientation - direction that boat will be positioned per user input (int)
#   Notes - maybe worth exploring splitting up this method??? Kinda big and does a lot 
    def checkBoatOrientation(self,selectedCell,boat, boatLength,uBoatOrientation):
        adjBoatPos = self.translateUserCell(selectedCell)
        redoInput = False
        print(f"\n this is your check that the correct orientation vector is being applied to your boat direction - {self.orientationOptions[uBoatOrientation]}\n"
        f"orientation select - {uBoatOrientation}\n" f"boat position, XY format {adjBoatPos}\n")
        PosFinal = [self.orientationOptions[uBoatOrientation][0]*(boatLength-1)+adjBoatPos[0],self.orientationOptions[uBoatOrientation][1]*(boatLength-1)+adjBoatPos[1]]
        print(f"final playing position {PosFinal}")
        #This is a stupid loop; you're checking both dimensions of the array, even if the first one fails
        for x in PosFinal:
            if x < 0 or x > len(self.gameBoard)-1:
                redoInput = True
        if redoInput:
            print("It seems like the orientation you tried to specify for your boat is not valid as it doesn't lie in the playing field; \n"
            "please try again or consider selecting a new starting position for your boat")
            self.specifyBoatOrientation(selectedCell,boat,boatLength)
        return PosFinal
            

#checkValidPositionInput will check the user's selection for orientation of their current boat; if the option isn't valid, it will prompt the user to give their position input again
#   selectedCell -> selectedCell is the user's starting boat position option
#   FUTURE WORK - have to check that user input is even a number; right now a string will cause an issue
    def checkValidPositionInput(self,selectedCell, boat, boatLength, uBoatOrientation):
        #recommendation - change self.orientationOptions to str(self.orientationOptions)
        if uBoatOrientation not in self.orientationOptions or len(uBoatOrientation) != 1:
            print("The input you have given for a boat orientation is not a valid option; please try again")
            self.specifyBoatOrientation(selectedCell, boat, boatLength)

#applyBoatOrientation places the boats on the playing board as specified by the player starting cell and the range of cells specified by user input for boat orientation
#   notes: this is stupid using if/else statement given that there's only 2 options; trying to figure out a way to make more concise 
    def applyBoatOrientation(self,uCell, endCell):
        uCellAdj = self.translateUserCell(uCell)
        if uCell[0] != endCell[0]:
            direction = self.applyBoatDirection(uCell[0]-endCell[0])
            
        else:
            direction = self.applyBoatDirection(uCell[1]-endCell[1])


    def applyBoatDirection(self,uCellDim,endCellDim):
        if endCellDim >= uCellDim:
            direction = 1
        else:
            direction = -1
        return direction

    def checkIntersection():
        pass



        


myBoard1 = Board()
myBoard2 = Board()
# testList = [myBoard1,myBoard2]
# print(testList)
# for x in testList:
#     print(myBoard1.shipHit)

testGame = Simulation(myBoard1,myBoard2)
testGame.runBoardSetupSteps()


#To do:
#   - build in functionality during ship position application to re-pick the cell position if desired 
#   - build placeBoats method
#       -actually, nontrivial process to have position be placed based on initial and final positions
#       - current recommendation: build in if statement to apply a positive or negative step to a range; then added position markers with this range that gets created
#   - current user input filtering will flag if a user puts a space between characters selected; might be worth having a method that allows spaces 
#   - need to create checkIntersection() method that will make sure boats aren't crossing