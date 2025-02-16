import numpy as np
import random
import time

class Simulation():
    def __init__(self,player1Board, player2Board):
        self.players = [player1Board,player2Board]
        self.clock = 0
        self.cpuAttackChoices = player1Board.cpuOptions #gives the self object the call to have all active places on the board 
        #These lists are used in cpu decision matrix to choose its next spot target
        self.cpuFollowup = [] #will be stored as list of lists such that the sublist are coordinates in the format [r,c]
        self.cpuVector = [] #will be stored as list of lists such that the sublist are coordinates in the format [r,c]
        self.version = 1.0

    def printGameHeader(self):
        print("----------------------------------------")
        print("|                                      |")
        print("|         WELCOME TO BATTLESHIP        |")
        print("|                                      |")
        print("----------------------------------------")

    def printGameInstructions(self):
        print(f"This is Battle Ship version {self.version}")
        print("The game is currently designed to be played against a CPU/n")
        print("The game will walk through the following stages\n   1) You will be prompted to place all your boats\n   2) You will take turns vs the CPU trying to hit the opponent's boats\n")
        print("PLEASE NOTE - your selections will need to be in the format - (letter)(number)\n     Example - A0,B5,etc...")
        print("Now let's get started; below, you will see the empty boards. The top will reflect your opponent's, and the bottom view is your board (where your boats will show up after you place them)")
        self.buildUserDisplay(playerTurn = 0)


    def runBoardBuilding(self):
        for x in self.players:
            for key, value in x.ships.items():
                if x.cpuOpponent:
                    x.cpuBoatPlacing(key,value)
                else:
                    self.playerBoardBuild(x,key,value) #should this function be a part of the board object instead of the Simulation object?

    def playerBoardBuild(self,player,key,value):
        userCellInput = player.userBoatPosPrompt(key,value)
        endBoatPoint = player.specifyBoatOrientation(userCellInput,key,value)
        #print(f"this is the end point being passed to applyBoatPosition {endBoatPoint}")
        player.applyBoatPosition(key,value,userCellInput,endBoatPoint, count = 0)

#playerTurn defines the ATTACKING player
#TO-DO:
#   - remove/finalize display visuals
    def cycleTurns(self,playerTurn):
        if self.clock ==0:
            self.startTurnsMessage()
        winCheck = False
        while not winCheck: 
            self.buildUserDisplay(playerTurn)
            userSelect = self.chooseAttackMethod(playerTurn)
            self.processTarg(userSelect,playerTurn)
            playerTurn = self.switchPlayer(playerTurn)
            winCheck = self.checkWinState(playerTurn,boatCount = 0, positionCount=0)
            self.clock += 1 #this is really stupid to have continuously adding just for the first turn to not trigger start message; consider better way of managing
            #print(f"Current state of winCheck - {winCheck}")
            #if not winCheck:
                #self.endTurnDisplay(self.switchPlayer(playerTurn))
    
    #endTurnDisplay just portrays the raw array - useful for testing 
    def endTurnDisplay(self,playerTurn):
        #print("This is the current state of the OPPOSING player's field (the one that just got SHOT AT)")
        #print(self.players[self.switchPlayer(playerTurn)].gameBoard)
        pass

    def promptPlayerAttack(self,turn):
        chosenCell = input(f"Player {turn+1} - Select the cell you want to hit. Your selection must be in the format of a '[Letter][Number]'") #The plus 1 here is necessary, as the index for the list is zero and 1; players are 1 and 2
        if not self.checkTargetInput(chosenCell,turn):
            chosenCell = self.promptPlayerAttack(turn)
        return chosenCell

    def chooseAttackMethod(self,playerTurn):
        if self.players[playerTurn].cpuOpponent is True:
            userSelect = self.cpuAttackTree(playerTurn)
            userSelect = self.translateCoordTarg([userSelect])
        else:
            userSelect = self.promptPlayerAttack(playerTurn)
        return userSelect


    def blindAttackSequence(self,playerTurn):
        iChoice = random.randint(0,len(self.cpuAttackChoices)-1)
        choice = self.cpuAttackChoices[iChoice]
        #This should be deleted later - being done to avoid the blind fire sequence at start of game for TESTING
        if self.clock <= 1:
            choice = 'C5'
            iChoice = self.cpuAttackChoices.index('C5')  
        cellChoice = self.translateUserTarg(choice)
        self.cpuAttackChoices.pop(iChoice) #removing it from further use in the future
        self.addToCPUFollowUps(cellChoice,playerTurn)
        return cellChoice 

    def cpuAttackTree(self,playerTurn):
        targetPlayer = self.switchPlayer(playerTurn)
        attackChoice = []
        #self.testingStartofAttackTree(attackChoice) 
        while len(attackChoice) < 1:
            if len(self.cpuFollowup) == 0:#option correleating with the cpu having no prior knowledge 
                #print("Currently trying a BLIND ATTACK")
                attackChoice.append(self.blindAttackSequence(playerTurn))
                destroyedBoatKey = self.players[targetPlayer].destroyedBoatStatus(attackChoice[0])
                if len(destroyedBoatKey) > 0: 
                    self.players[targetPlayer].destroyedBoatPos[destroyedBoatKey[0]] 

            elif len(self.cpuVector) == 0: #picking a random option from followUp
                print("Currently Trying FOLLOW Attack")
                self.cpuFollowUpSeq(attackChoice,playerTurn)
                destroyedBoatKey = self.players[targetPlayer].destroyedBoatStatus(attackChoice[0])
                if len(destroyedBoatKey) > 0: 
                    self.players[targetPlayer].destroyedBoatPos[destroyedBoatKey[0]]
            else:
                #print("Currently Trying a VECTOR attack")
                self.vectorBasedAttack(attackChoice,playerTurn)
                #self.testingEndofVectorAttack(attackChoice)

        #print(f"This is the variable being returned from cpuAttackTree {attackChoice[0]}")
        return attackChoice[0]
    
    def testingEndofVectorAttack(self,attackChoice):
        print(f"You are about to exit vectorBasedAttack portion of your tree\n attack choice - {attackChoice}  \n current state of vector - {self.cpuVector} n\current state of followUp - {self.cpuFollowup} ")
        input("Hit Enter when ready to progress")

    def testingStartofAttackTree(self,attackChoice):
        print(f"You are about to enter the beginning of attack tree\n attack choice - {attackChoice}  \n current state of vector - {self.cpuVector} n\current state of followUp - {self.cpuFollowup} ")
        input("Hit Enter when ready to progress")

    def cpuFollowUpSeq(self,attackChoice,playerTurn):
        # print("\nThis is you Enterinng the cpuFollowUpSeq")
        # print(f"This is the current class variable, cpuFollowup - {self.cpuFollowup}\n This is the value at index of zero - {self.cpuFollowup[0]}")
        rootCellTarget = self.cpuFollowup[0]
        attackChoice.append(self.cpuUndirectedFollowUp(rootCellTarget,playerTurn))
        if len(attackChoice) < 1:
            self.cpuFollowup.pop[0]
        else:
            print(f"This is at end of FollowUpSeq:\n This is your attack choice being passed to vectorCheck function {attackChoice}")
            self.vectorCheck(self.cpuFollowup[0],attackChoice[0],playerTurn)
        
    def vectorCheck(self,currentRoot, targetCell,playerTurn):
        if self.players[0].gameBoard[tuple(targetCell)] == self.players[0].shipSafe:
            if len(self.cpuVector) > 0:
                self.cpuVector.append(targetCell)
            else:
                self.cpuVector.append(currentRoot)
                self.cpuVector.append(targetCell)

#This will literally only work for blind firing sequence, since for the vector sequence you're already going to have the battle ship be hit by the time you need to pass v
#   NEED TO THINK OF ANOTHER WAY TO GO ABOUT THIS
    def addToCPUFollowUps(self,hitList,playerTurn):
        #print(f"This is what's being passed to addToCPUFollowUps - {hitList}")
        targetPlayer = self.switchPlayer(playerTurn)
        coordTest = self.players[targetPlayer].gameBoard[tuple(hitList)]
        #print(coordTest)
        if coordTest == self.players[playerTurn].shipSafe:
            self.cpuFollowup.append(hitList)

    #cpuUndirectedFollowUp just goes through the process of calling necessary functions to get a successful follow-up cell to attack  
    def cpuUndirectedFollowUp(self,rootCell,playerTurn):
        targetPlayer = self.switchPlayer(playerTurn)
        #followupCell = []
        cpuDirectionOpts = [str(x) for x in range(1,5)]
        redoInput = True
        while redoInput is True:
            hashDirectionIndex = (random.randint(0,len(cpuDirectionOpts)-1))
            #print(f"\nYou are now in cpuUndirectedFollowUp\n Your selected hashDirectionIndex is {hashDirectionIndex}\n Your current cpuDirectionOpts - {cpuDirectionOpts}") #delete later as this as part of TESTING
            followupCell = self.chooseAdjacentCell(rootCell,cpuDirectionOpts,hashDirectionIndex)
            redoInput = self.cpuCheckNextShotValid(followupCell,targetPlayer)
        return followupCell

#chooseAdjacentCell will select next random direction to go from a cpuFollowUp
    def chooseAdjacentCell(self, rootCell,cpuAvailDirections,hashDirectionIndex):
        directionVectors = self.players[0].orientationOptions
        #print(f"You are now in choose Adjacent Cell:\n These are your directionVectors option list from a Board Object - {directionVectors}\n This is the type of your directionVectors options - {type(directionVectors)}")
        #adjCell = self.translateUserTarg(rootCell)
        dictNavigator = cpuAvailDirections[hashDirectionIndex]
        directionChoice = directionVectors[dictNavigator]
        chosenCell = [rootCell[x] + directionChoice[x] for x in range(len(directionChoice))]
        cpuAvailDirections.pop(hashDirectionIndex)
        return chosenCell

#cpuCheckNextShotValid will take an input in the [r,c] format  and determine whether the option is in the proper format
#Note - nextChoice(list) here definitely implies the need for something in the format [row,column]
#Return - redoInput (boolean): Gives response if next shot is a valid option {true} or if it needs to be selected again {false}
    def cpuCheckNextShotValid(self, nextChoice,targetPlayer):
        redoInput = False
        for x in nextChoice:
            if x < 0 or x > len(self.players[0].boardRows)-1:
                redoInput = True
        if redoInput is False:
            boardState = self.players[targetPlayer].gameBoard[tuple(nextChoice)]
            if boardState == self.players[targetPlayer].emptySpotHit or boardState == self.players[targetPlayer].shipHit:
                redoInput = True
        return redoInput

#nextVectorShot will return the next target on the board based on what options are available adjacent to targets in the cpu's vector range
    def nextVectorShot(self,attackChoice,targetPlayer):
        currentDirectionIndex = self.getVectorDirectionIndex() #currentDirection is given as a 2-dim list that will apply the direction to the vector search
        adjacentTargets = self.calculateVectorExtensions(currentDirectionIndex,targetPlayer)
        if len(adjacentTargets)>0:
            attackChoice.append(adjacentTargets[0])
            #Find a better way to call the currently targeted spot by the cpu - Object call here looks UGLY
            #purpose if this call is only to add a cell to cpuVector instance variable IF the target is a HIT
            if self.players[targetPlayer].gameBoard[tuple(adjacentTargets[0])] == self.players[targetPlayer].shipSafe:
                self.cpuVector.append(adjacentTargets[0])

    def vectorBasedAttack(self,attackChoice,playerTurn):
        oppositePlayer = self.switchPlayer(playerTurn)
        self.nextVectorShot(attackChoice,oppositePlayer)
        positionsDeletingFromVector = []
        if len(attackChoice)>0:
            positionsDeletingFromVector = (self.getObsoleteVectorPos(attackChoice[0],oppositePlayer))
        self.closeVectorTargs(attackChoice,oppositePlayer,positionsDeletingFromVector)

#getObsoleteVectorPos will call the Board's object function destroyedBoatStatus; which will add target cell to dict of hit boat positions as an instance variable
#   return - usedPositions: list of positions that represent the cells that contributed to a boat being destroyed. list of sublists in the format [r,c]
    def getObsoleteVectorPos(self,targetCell,targetPlayer):
        usedPositions = []
        destroyedBoatKey = self.players[targetPlayer].destroyedBoatStatus(targetCell)
        if len(destroyedBoatKey) > 0:
            usedPositions = (self.players[targetPlayer].destroyedBoatPos[destroyedBoatKey[0]]) 
        return usedPositions


#most of closeVectorTargs should be different functions since it gets reused - consider revisiting
#FUTURE WORK:
#   Consider a way to make less stupid
    def closeVectorTargs(self,attackChoice,targetPlayer,finishedBoatPositions):
        #input(f"You have entered closeVectorTargs - this is currently your vector {self.cpuVector}.\n This is currently your attack choice - {attackChoice[0]} \nHIT ENTER WHEN YOURE READY TO CONTINUE")
        #input(f"This is your finishedBoatPositions; it should be empty - {finishedBoatPositions}\n HIT ENTER WHEN READY TO CONTINUE")
        if len(attackChoice)>0 and len(finishedBoatPositions)>0:
            print(len(finishedBoatPositions[0]))
            for vectorPosition in finishedBoatPositions:
                input("You are entering the portion where you're removing the destroyed positions from your vector list")
                self.cpuVector.remove(vectorPosition)
                if self.translateCoordTarg([vectorPosition]) in self.cpuAttackChoices:
                    self.cpuAttackChoices.remove(self.translateCoordTarg([vectorPosition]))
                if vectorPosition in self.cpuFollowup:
                    self.cpuFollowup.remove(vectorPosition)
        elif len(attackChoice) < 1:
            for vectorPosition in self.cpuVector[:]:
                self.cpuVector.remove(vectorPosition)
                if vectorPosition not in self.cpuFollowup: #this is adding the vector elements to follow-up
                    self.cpuFollowup.append(vectorPosition)
                if self.translateCoordTarg([vectorPosition]) in self.cpuAttackChoices:
                    self.cpuAttackChoices.remove(self.translateCoordTarg([vectorPosition]))                
        #input(f"This is the end of you closing your first vector target; current state of vector - {self.cpuVector}")

#this way of assigning the vector extension is UNBELIVABLY headass - like make a loop bro
#Notes - vectorOptions is going to return the ends of the current attack vector through which the cpu is searching 
#   -Remember, if the list comes back empty, it's because no targets are currently valid from the possible vector extensions. In which case, the list  cpuFollowup list 
#       needs to be referenced to choose next attack targets
#   - Parameters:
#       -i - given from getVectorDirectionIndex; gives the direction of the boat in which you're attacking 
    def calculateVectorExtensions(self,index,targetPlayer):
        oppositeindex = 1-index #index tells you which direction you want to increment by +/- 1 to find additional boat locations; opposite index will stay constant
        #print(f"YOU HAVE ENTERED calculateVECTOR EXTENSIONS :\n This is your vector as of now - {self.cpuVector}\n This is your index of attack as of now - {index}")
        highValue = self.cpuVector[0][oppositeindex]
        lowValue = self.cpuVector[0][oppositeindex]
        highCell = [0,0]
        lowCell = [0,0]
        for x in range(len(self.cpuVector)):
            highValue = max(highValue, self.cpuVector[x][oppositeindex])
            lowValue = min(lowValue,self.cpuVector[x][oppositeindex])
        highCell[index] = self.cpuVector[0][index]
        highCell[oppositeindex] = highValue+1
        lowCell[index] = self.cpuVector[0][index] 
        lowCell[oppositeindex] = lowValue-1
        vectorOptions = [highCell,lowCell] 
        #print(f"THESE ARE THE OPTIONS BEING PASSED TO deleteInvalidVectorExtensions - {vectorOptions}")
        validVectorOptions = self.deleteInvalidVectorExtensions(vectorOptions,targetPlayer)
        #input(f"THESE ARE THE OPTIONS YOU ARE PICKING AS VALID VECTOR EXTENSIONS - {validVectorOptions}; PRESS ENTER TO CONTINUE")
        return validVectorOptions
    
    def  deleteInvalidVectorExtensions(self,vectorOptions,targetPlayer):
        for index in range(len(vectorOptions)-1,-1,-1):
            if self.cpuCheckNextShotValid(vectorOptions[index],targetPlayer):
                vectorOptions.pop(index)
        return vectorOptions


    #getVectorDirectionIndex tells you which dimension (rows or columns) the ship is moving along
    #return i - whether the current targets of boat is moving alonng boat or lines 
    def getVectorDirectionIndex(self):
        findingIndex = True
        i = 0
        while findingIndex is True:
            if self.cpuVector[0][i] == self.cpuVector[1][i]:
                findingIndex = False
            else:
                i += 1
        return i

    def processTarg(self,selectCell,turn): 
        successfulTurn = False #successful turn only counts if a turn doesn't need to be repeated because someone has selected a cell that already has been targeted before
        playerTarg = self.players[self.switchPlayer(turn)]
        #print(f"The player that is getting HIT is Player{self.switchPlayer(turn)+1}")
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
            self.processTarg(selectCell,turn)

#translateUserTarg takes the input of something in the string format 'X#' and returns a coordinate that can be placed on the numpy gameBoard array tied to a Board object  
    def translateUserTarg(self,uInput):
        print(uInput)
        variable = [self.players[0].boardRows.index(uInput[0]),int(uInput[1])]
        return variable

#translateCoordTarg takes parameter Input (list) in the format [r,c] and translates it to the battleship coordinate game format (string "x#")
    def translateCoordTarg(self,input):
        translatedCoords = []
        for x in input:
            print(input)
            rows = self.players[0].boardRows[x[0]]
            columns = self.players[0].boardColumns[x[1]]
            translatedCoords.append(rows+columns)
        return translatedCoords[0]

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


    def checkWinState(self,turn,boatCount,positionCount):
        targetPlayer = self.switchPlayer(turn) 
        win = True 
        boatItems = iter(self.players[targetPlayer].storedPositions.items())
        for boat,positions in self.players[targetPlayer].storedPositions.items():
            if sorted(self.players[targetPlayer].destroyedBoatPos[boat]) != sorted(positions):
                win = False
        return win
    
    def informGameEnd(gameCheck,turn):
        if gameCheck:
            print(f"The game is over - Player {turn} has won!!! Thank you for playing")

    def switchPlayer(self,turn):
        return abs(1-turn)

    def startTurnsMessage(self):
        print("All boats have been placed - this is the start of the turns; Player 1 will be first for selecting cells")

#Notice how playerTurn gets defined in cycleTurns() function - 0 means that player 1 is attacking first 
    def playGameTest(self):
        self.printGameHeader()
        self.printGameInstructions()
        #self.runBoardBuilding()
        #print(self.players[0].cpuOptions)
        self.runBoardBuilding()
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
         

    def drawTestBoards(self):
        for x in self.players:
            for key,value in x.storedPositions.items():
                for y in value:
                    x.gameBoard[tuple(y)] = x.shipSafe

    def testBoardBuilding(self):
        self.defineTestBoards()
        self.drawTestBoards()

    def testCPUBoardBuilding(self):
        for key, value in self.players[0].ships.items():
            self.players[0].cpuBoatPlacing(key,value)
        print(f"see player one board:\n {self.players[0].gameBoard}")
        print(self.players[0].storedPositions)
        #print(f"see player two board:\n {self.players[1].gameBoard}")

    def buildUserDisplay(self,playerTurn):
        if self.players[playerTurn].cpuOpponent is not True:
            columns = self.drawColumnHeader(playerTurn)
            divider = self.drawColumnDivider(columns)   
            print("Your view of opponenet:")
            print(columns)
            print(divider)
            self.drawingTargetPlayerBoard(playerTurn)
            print("\n")
            print("Your view:")
            print(columns)
            print(divider)
            self.drawingCurrentPlayerBoard(playerTurn)

    def drawColumnHeader(self,playerTurn):
        columnHeader = "   | "
        for col in self.players[0].boardColumns:
            extension = str(col) + "  "
            columnHeader += extension
        return columnHeader
    
    def drawColumnDivider(self,columnHeader):
        divider = "_"
        for unit in range(len(columnHeader)):
            divider += "_"
        return divider 


    def drawingCurrentPlayerBoard(self,playerTurn):
        currentPlayerBoard = self.players[playerTurn].gameBoard
        rowToPrint = ""
        for rows in range(len(self.players[0].boardRows)):
            rowToPrint = " " + self.players[0].boardRows[rows] + " | "
            for col in range(len(self.players[0].boardColumns)):
                if currentPlayerBoard[rows][col] == 0 or currentPlayerBoard[rows][col] == 3:
                    addValue = "O"
                elif currentPlayerBoard[rows][col] == 1: 
                    addValue = "S"
                elif currentPlayerBoard[rows][col] == 2:
                    addValue = "X"
                rowToPrint += addValue +"  "
            print(rowToPrint)

    def drawingTargetPlayerBoard(self,playerTurn):
        targetPlayer = self.switchPlayer(playerTurn)
        targetPlayerBoard = self.players[targetPlayer].gameBoard
        for rows in range(len(self.players[0].boardRows)):
            rowToPrint = " " + self.players[0].boardRows[rows] + " | "
            for col in range(len(self.players[0].boardColumns)):
                if targetPlayerBoard[rows][col] == 0 or targetPlayerBoard[rows][col] == 1:
                    addValue = " "
                elif targetPlayerBoard[rows][col] == 3: 
                    addValue = "O"
                elif targetPlayerBoard[rows][col] == 2:
                    addValue = "X"
                rowToPrint += addValue +"  "
            print(rowToPrint)


class Board:
    def __init__(self,cpuSelect):
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
        "Carrier":[],
        "Battle Ship":[],
        "Destroyer":[],
        "Submarine":[],
        "Patrol Boat":[]
        }

        self.destroyedBoatPos = {
        "Carrier":[],
        "Battle Ship":[],
        "Destroyer":[],
        "Submarine":[],
        "Patrol Boat":[]
        } 

        self.cpuOpponent = cpuSelect
        self.cpuOptions = [x + y for x in self.boardRows for y in self.boardColumns]
        self.cpuUsedCells = []
    
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
        PosFinal = [self.orientationOptions[uBoatOrientation][0]*(boatLength-1)+adjBoatPos[0],self.orientationOptions[uBoatOrientation][1]*(boatLength-1)+adjBoatPos[1]]
        for x in PosFinal:
            if x < 0 or x > len(self.gameBoard)-1:
                redoInput = True
        if redoInput:
            print("It seems like the orientation you tried to specify for your boat is not valid as it doesn't lie in the playing field; \n"
            "please try again or consider selecting a new starting position for your boat")
            PosFinal = self.specifyBoatOrientation(selectedCell,boat,boatLength)  
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
            if self.checkIntersection(boat,boatLength,allBoatCoords):
                for x in allBoatCoords:
                    self.gameBoard[tuple(x)] = self.shipSafe
                self.storeBoatPos(boat,allBoatCoords)
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

#cpuBoatPlacing will assigned the used cells to consumedCells list 
    def cpuBoatPlacing(self,boat,boatLength):
        print("\n\nThe CPU Opponent will now select their board layout:")
        print(f"Boat - {boat}; boat length - {boatLength}")
        print(f"This is what the cpu has used at the start of this boat {self.cpuUsedCells}")
        placingBoat = True
        while placingBoat:
            print("stuck in cbp")
            time.sleep(1)
            selectCell = self.cpuOptions[random.randint(0,(len(self.cpuOptions)-1))]
            finalCell = self.cpuBoatOrientation(selectCell,boat,boatLength)
            placingBoat = self.applyCPUBoats(boat,boatLength,selectCell,finalCell,placingBoat, count = 0)
        
        
    def cpuBoatOrientation(self,selectCell,boat,boatLength):
        cpuOrientationOpts = [str(x) for x in range(1,5)]
        choosingOrientation = True
        while choosingOrientation:
            indexSelect = random.randint(0,(len(cpuOrientationOpts)-1))
            selectOrient = cpuOrientationOpts[indexSelect]
            PosFinal = self.calCPUPosFinal(selectCell,boatLength,selectOrient)
            if self.checkCPUOrientation(PosFinal):
                cpuOrientationOpts.pop(indexSelect)
            else:
                choosingOrientation = False
        return PosFinal

    def calCPUPosFinal(self,selectedCell,boatLength,cpuOrientation):
        adjBoatPos = self.translateUserCell(selectedCell)
        print(adjBoatPos)
        print(cpuOrientation)
        return [self.orientationOptions[cpuOrientation][0]*(boatLength-1)+adjBoatPos[0],self.orientationOptions[cpuOrientation][1]*(boatLength-1)+adjBoatPos[1]]

    def checkCPUOrientation(self,PosFinalTest):
        redoInput = False
        for x in PosFinalTest:
            if x < 0 or x > len(self.gameBoard)-1:
                redoInput = True
        return redoInput

    def applyCPUBoats(self,boat,boatLength,uCell,endCell,placingBoatCheck,count):
        adjBoatPos = self.translateUserCell(uCell)
        if adjBoatPos[count] != endCell[count]:
            boardCoord = [x for x in adjBoatPos] 
            allBoatCoords = self.getBoatCoords(boardCoord,adjBoatPos,endCell,count)
            print(f"This is all the potential boat coordinates being assessed for placement (determined in applyCPUBoats): {allBoatCoords}")
            runIntersectCheck = self.cpuIntersectPass(allBoatCoords)
            if runIntersectCheck:
                for x in allBoatCoords:
                    self.gameBoard[tuple(x)] = self.shipSafe
                self.storeBoatPos(boat,allBoatCoords)
                placingBoatCheck = False
                self.addCPUList(allBoatCoords)
            else:
                print("cpu tried placing cell on existing boat; the cpu will be forced to select again")
        else:
            count += 1 
            placingBoatCheck = self.applyCPUBoats(boat,boatLength,uCell,endCell,placingBoatCheck,count)
        return placingBoatCheck
        
    def addCPUList(self,finalizedBoatCoords):
        for x in finalizedBoatCoords:
            self.cpuUsedCells.append(x)

    def cpuIntersectPass(self,potentialSpots):
        print(f"This is all the potential boat coordinates being assessed for placement (passed to checkIntersectPass): {potentialSpots}")
        validPlacement = True
        count = 0
        while validPlacement and count<len(potentialSpots):
            if potentialSpots[count] in self.cpuUsedCells:
                validPlacement = False
            count +=1 
        print(f"This is the boolean being returned by cpuIntersectPass - {validPlacement}")
        return validPlacement
    
#destroyedBoatStatus will return a list, where if a boat was destroyed by selection of "targetCell", the list will contain boat name that was destroyed
#     return - list containing the name of the boat that was destroyed by most recent target Cell 
# parameters:
#   - targetCell - list in the format [r,c]; represents row and column position on game board matrix
    def destroyedBoatStatus(self,targetCell):
        # print(f"You have entered destroyedBoatStatus - this is the target cell being evaluated")
        #input(f"This is the current status of your destroyed boats in the Board object {self.destroyedBoatPos}")
        deleteBoatKey = []
        for boat, positions in self.storedPositions.items():
            if targetCell in positions:
                self.destroyedBoatPos[boat].append(targetCell)
                #input(f"YOU HAVE ADDED A POSITION TO THE HIT DESTROYED BOAT POS - this is your destroyedBoatPos: {self.destroyedBoatPos}")
                if sorted(self.destroyedBoatPos[boat]) == sorted(positions): #just recently added sorted() to this line, not sure if it'll work
                    deleteBoatKey.append(boat)
        if len(deleteBoatKey)>0:
            self.destroyedBoatMes(deleteBoatKey[0])
        #     self.storeBoatPos.pop(deleteBoatKey[0]) Cant figure out why this line of code is here
        return deleteBoatKey

    def destroyedBoatMes(self,boat):
        print(f"You have destroyed the opponents {boat}!!!")

cpuState = True
myBoard1 = Board(False)
myBoard2 = Board(True)

testGame = Simulation(myBoard1,myBoard2)
testGame.playGameTest()


