import numpy as np
import pandas as pd

class Simulation():
    def __init__(self,player1Board, player2Board):
        self.players = [player1Board,player2Board]
        self.clock = 0

    
#Note - currently refabbing to make all these functions get called within other Board object methods
    def runBoardBuilding(self):
        print(self.players)
        for x in self.players:
            for key, value in x.ships.items():
                userCellInput = x.userBoatPosPrompt(key,value)
                endBoatPoint = x.specifyBoatOrientation(userCellInput,key,value)
                print(f"this is the end point being passed to applyBoatPosition {endBoatPoint}")
                x.applyBoatPosition(key,value,userCellInput,endBoatPoint, count = 0)


#playerTurn defines the ATTACKING player
#TO-DO:
#   - remove/finalize display visuals
    def cycleTurns(self,playerTurn):
        if self.clock ==0:
            self.startTurnsMessage()
        winCheck = False
        while not winCheck:
            userSelect = self.promptPlayerAttack(playerTurn)
            self.processTarg(userSelect,playerTurn)
            playerTurn = self.switchPlayer(playerTurn)
            winCheck = self.checkWinState(playerTurn,boatCount = 0, positionCount=0)
            self.clock += 1 #this is really stupid to have continuously adding just for the first turn to not trigger start message; consider better way of managing
            self.endTurnDisplay(playerTurn)
    
    def endTurnDisplay(self,playerTurn):
        print("This is the current state of the OPPOSING player's field (the one that just got SHOT AT)")
        print(self.players[self.switchPlayer(playerTurn)].gameBoard)


    def promptPlayerAttack(self,turn):
        chosenCell = input(f"Player {turn+1} - Select the cell you want to hit. Your selection must be in the format of a '[Letter][Number]'") #The plus 1 here is necessary, as the index for the list is zero and 1; players are 1 and 2
        if not self.checkTargetInput(chosenCell,turn):
            chosenCell = self.promptPlayerAttack(turn)
        return chosenCell

    def processTarg(self,selectCell,turn): 
        successfulTurn = False #successful turn only counts if a turn doesn't need to be repeated because someone has selected a cell that already has been targeted before
        playerTarg = self.players[self.switchPlayer(turn)]
        matrixCell = self.translateUserTarg(selectCell) #where target is in format that can be passed to np matrix
        if playerTarg.gameBoard[tuple(matrixCell)] == playerTarg.emptySpot:
            print("You've missed the target")
            playerTarg.gameBoard[tuple(matrixCell)] = playerTarg.emptySpotHit
            successfulTurn = True
        elif playerTarg.gameBoard[tuple(matrixCell)] == playerTarg.shipSafe:
            print("You've HIT a target")
            playerTarg.gameBoard[tuple(matrixCell)] = playerTarg.shipHit
            successfulTurn = True
        elif playerTarg.gameBoard[tuple(matrixCell)] == playerTarg.shipHit:
            print("This is already a spot where you've scored a hit - please try again:")
        elif playerTarg.gameBoard[tuple(matrixCell)] == playerTarg.emptySpotHit:
            print("You've already missed here before - please try selecting again")
        if not successfulTurn:
            selectCell = self.promptPlayerAttack(turn)
            self.processTarg(selectCell)


    def translateUserTarg(self,uInput):
        return (self.players[0].boardRows.index(uInput[0]),int(uInput[1]))


    def checkTargetInput(self,uInput,turn):
        inputCheck = list(uInput.upper())
        continueSelection = False
        if len(inputCheck) != 2:
            print("your input isn't in the correct 2 digit format, please try again")
        elif inputCheck[0] not in self.players[turn].boardRows:
            print("Your first digit is not in the proper letter format for cell rows; please try again")
        elif inputCheck[1] not in self.players[turn].boardColumns:
            print("your second digit reprsenting your column selection was incorrect; please try again")
        else:
            continueSelection = True 
        return continueSelection

#this can be optimizaed to stop after it finds a single surviving boat cell
    def checkWinState(self,turn,boatCount,positionCount):
        win = True 
        boatItems = iter(self.players[turn].storedPositions.items())
        while boatCount < len(self.players[turn].storedPositions) and win ==True:
            key,currBoatPos = next(boatItems)
            while positionCount < len(currBoatPos) and win == True:
                if self.players[turn].gameBoard[tuple(currBoatPos[positionCount])] == self.players[turn].shipSafe:
                    win = False
                else: #This else portion is added to just track how the function is running; should be removed after game is finalized/tested
                    print("Game has not been won by current player - play will continue") 
                positionCount += 1
            boatCount +=1
        return win
    
    def informGameEnd(gameCheck,turn):
        if gameCheck:
            print(f"The game is over - Player {turn} has won!!! Thank you for playing")

    def switchPlayer(self,turn):
        return abs(1-turn)

    def startTurnsMessage(self):
        print("All boats have been placed - this is the start of the turns; Player 1 will be first for selecting cells")

    def playGameTest(self):
        #self.runBoardBuilding()
        self.testBoardBuilding()
        # print(self.players[0].gameBoard)
        # print(self.players[0].storedPositions)
        self.cycleTurns(playerTurn=0)


#defineTestBoards will set the game board for battle ship with predetermined game board; makes it easier than playing through the first part of the game every time 
    def defineTestBoards(self):
        player1TestBoats = {
        "Carrier":[[0,5],[1,5],[2,5],[3,5],[4,5]],
        "Battle Ship":[[1,4],[2,4],[3,4],[4,4]],
        "Destroyer":[[1,3],[2,3],[3,3]],
        "Submarine":[[1,2],[2,2],[3,2]],
        "Patrol Boat":[[1,1],[2,1]]
        }

        player2TestBoats = {
        "Carrier":[[9,5],[8,5],[7,5],[6,5],[5,5]],
        "Battle Ship":[[9,4],[8,4],[7,4],[6,4]],
        "Destroyer":[[9,3],[8,3],[7,3]],
        "Submarine":[[9,2],[8,2],[7,2]],
        "Patrol Boat":[[9,1],[9,1]]
        }
        self.players[0].storedPositions = player1TestBoats
        self.players[1].storedPositions = player2TestBoats
        return 

    def drawTestBoards(self):
        for x in self.players:
            for key,value in x.storedPositions.items():
                for y in value:
                    x.gameBoard[tuple(y)] = x.shipSafe

    def testBoardBuilding(self):
        self.defineTestBoards()
        self.drawTestBoards()

class Board:
    def __init__(self):
        self.emptySpot = 0
        self.shipSafe = 1
        self.shipHit = 2
        self.emptySpotHit = 3
        self.gameBoard = np.zeros((10,10))
        self.boardRows = list("ABCDEFGHIJ")
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
            '1':[-1,0],          
            '2':[0,1],
            '3':[1,0],
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
#   Notes: This is a difficult one; the if statement checking for '5' can't seem to be it's own function since it would need to return the selectedCell AND endCellCheck
#       Recommendation - tie checkValidPositionInput into promptOrientationSelect so it can all be handeled in one method call in specifyBoatOrientation
    def specifyBoatOrientation(self, selectedCell, boat, boatLength):
        #print("Select the direction you will place your boat (if the boat is found to go over the edge of the board, you will be asked to redo the input)")
        orientationSelect = self.promptOrientationSelect(selectedCell)
        #print(f"\n\n This is your check to see why your option isn't being selected:\n user input {orientationSelect}\n type {type(orientationSelect)}\n \n \n") #testing user orientation input
        print(f"This is the user input for orientation that's going into the checkValidPosition Input AND checkBoatOrientation ===> {orientationSelect}")
        if orientationSelect == '5':
            print("Please make your new selection for the starting point of your boat")
            selectedCell = self.userBoatPosPrompt(boat,boatLength)
            endCellCheck = self.specifyBoatOrientation(selectedCell,boat,boatLength)
        else:
            orientationSelect = self.checkValidPositionInput(selectedCell,boat,boatLength,orientationSelect) 
            endCellCheck = self.checkBoatOrientation(selectedCell,boat,boatLength,orientationSelect)
        #print(f"this is the position that is being DEFINITEVLY returned to the Simulation object ===> {endCellCheck}")
        return endCellCheck

#Notes: Put promptOrientationSelect such that it returns orientationChoice if the check comes out bad
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
        #print(f"\n this is your check that the correct orientation vector is being applied to your boat direction - {self.orientationOptions[uBoatOrientation]}\n"
        #f"orientation select - {uBoatOrientation}\n" f"boat position, XY format {adjBoatPos}\n")
        PosFinal = [self.orientationOptions[uBoatOrientation][0]*(boatLength-1)+adjBoatPos[0],self.orientationOptions[uBoatOrientation][1]*(boatLength-1)+adjBoatPos[1]]
        #print(f"final playing position being captured in checkBoatOrientation ===> {PosFinal}\n\n")
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
#   More pressing future work >>>> you can't do everything in this function; need to split functionality of checking for a '5' input vs a VALID input option
    def checkValidPositionInput(self,selectedCell, boat, boatLength, uBoatOrientation):
        if uBoatOrientation not in self.orientationOptions or len(uBoatOrientation) != 1:
            print("The input you have given for a boat orientation is not a valid option; please try again")
            uBoatOrientation = self.promptOrientationSelect(selectedCell)
            uBoatOrientation = self.checkValidPositionInput(selectedCell,boat,boatLength,uBoatOrientation)
        return uBoatOrientation

#applyBoatPosition places the boats on the playing board as specified by the player starting cell and the range of cells specified by user input for boat orientation
    def applyBoatPosition(self,boat,boatLength,uCell,endCell,count):
        adjBoatPos = self.translateUserCell(uCell)
        if adjBoatPos[count] != endCell[count]:
            boardCoord = [x for x in adjBoatPos] 
            allBoatCoords = self.getBoatCoords(boardCoord,adjBoatPos,endCell,count)
            #print(f"these are the variables being passed to checkIntersection:\n boat - {boat}\n boatLength - {boatLength}\n Coords - {allBoatCoords}")
            if self.checkIntersection(boat,boatLength,allBoatCoords):
                for x in allBoatCoords:
                    self.gameBoard[tuple(x)] = self.shipSafe
                print(self.gameBoard) #testing if applyBoatPosition is working 
                self.storeBoatPos(boat,allBoatCoords)

        else:
            #print("If this triggers something REALLY wrong is happening lol")
            count += 1 
            self.applyBoatPosition(boat,boatLength,uCell,endCell,count)

#getBoatCoords returns a LIST of all the points that will be placed on the game board as part of a single boat 
    def getBoatCoords(self,boatCoord,adjBoatPos,endCell,count):
        allBoatCoords = []
        direction = self.findBoatDirection(adjBoatPos[count],endCell[count])
        for x in range(adjBoatPos[count],endCell[count]+direction,direction):
            boatCoord[count] = x
            allBoatCoords.append(boatCoord[:])
            #print(allBoatCoords)
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
#   Note - it checks all the points of potentialCoords, but really it should stop after 1 check
    def checkIntersection(self, boat, boatLength, potentialCoords):
        #print(f"This is coords checkIntersection actually sees - {potentialCoords}")
        intersectState = True
        count = 0
        for x in potentialCoords:
            if self.gameBoard[tuple(x)] == self.shipSafe and intersectState: 
                intersectState = False
                self.intersectMessage()
                uCell = self.userBoatPosPrompt(boat,boatLength)
                endCell = self.specifyBoatOrientation(uCell,boat,boatLength)
                self.applyBoatPosition(boat,boatLength,uCell,endCell, count=0)
                count +=1 
        return intersectState

    def intersectMessage(self):
        print("It seems like you've placed a boat such that it overlaps with an existing boat on the board; please start again and try picking a new position for this current boat:")
    
    
    def storeBoatPos(self,boat,finalBoatCoords):
        self.storedPositions[boat] = finalBoatCoords

myBoard1 = Board()
myBoard2 = Board()

testGame = Simulation(myBoard1,myBoard2)
testGame.playGameTest()



#To do:
#   - test functionality during ship position application to re-pick the cell position if desired 

#   - current user input filtering will flag if a user puts a space between characters selected; might be worth having a method that allows spaces 
#   - test intersection detecting capabilities 

#   checkValidPositionInput is SO dumb right now -should make the prompt for position input it's own function so that you can call it more easily
#       - since it's tied to specifyBoatOrientation it makes it difficult to recursively correct 

