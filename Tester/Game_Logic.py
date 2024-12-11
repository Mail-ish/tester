from enum import Enum
from Player import *


class Status(Enum):
    ONGOING = 1
    WIN = 2
    TIE = 3

class GameStatus:
    def __init__(self):
        self.status = Status.ONGOING

    def updateGameStatus(self, newStatus):
        self.status = newStatus

class GameboardLogic:
    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]

    def __del__(self):
    # Destructor for cleanup when quitting the game
        print("game obj destroyed")
   
    def isCellEmpty(self, row, col):
        if row < 0 or row >= 3 or col < 0 or col >= 3:
            raise IndexError("Invalid cell indices")
        return (self.board[row][col] == '')

    def placeMark(self, row, col, mark):
        if self.isCellEmpty(row, col):
            self.board[row][col] = mark
        else:
            print("Cell is occupied, choose another cell. \n")
            return

    def checkWinCondition(self):
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] != '':  # check each element of a row
                return True

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != '':
                return True

        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != '':
            return True
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != '':
            return True
        else:
            return False

    def checkTieCondition(self):
        for row in self.board:
            if '' in row:
                return False

        if self.checkWinCondition():
            return False
        else:
            return True

    def getWinningLine(self):
        for i, row in enumerate(self.board):  # to give number to each row so that it can returned
            if row[0] == row[1] == row[2] and row[0] != '':
                winningLine = f"Row {i}"
                return winningLine

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != '':
                winningLine = f"Column {col}"
                return winningLine

        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != '':
            winningLine = f"Diagonal (top-left to bottom-right)"
            return winningLine
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != '':
            winningLine = f"Diagonal (top-right to bottom-left)"
            return winningLine
        else:
            print("Error finding a winning line!!")
            return None

    def resetBoard(self):
        """Resets the game board to an empty state."""
        self.board = [['' for _ in range(3)] for _ in range(3)] # Reset all cells to empty



class GameLogic:
    def __init__(self, Player_1, Player_2):
        self.board = GameboardLogic()
        self.player1 = Player_1
        self.player2 = Player_2
        self.startingPlayer = self.player1
        self.currentPlayer = self.startingPlayer
        self.gameStatus = GameStatus()

    def validateMove(self, row, col):
        self.board.placeMark(row, col, self.currentPlayer.getMark())
        if self.board.checkWinCondition():
            self.gameStatus.updateGameStatus(Status.WIN)
            self.currentPlayer.addWin()
            self.board.getWinningLine()
        elif self.board.checkTieCondition():
            self.gameStatus.updateGameStatus(Status.TIE)
            self.player1.addTie()
            self.player2.addTie()

    def switchTurn(self):
        if self.currentPlayer is self.player1:
            self.currentPlayer = self.player2
        else:
            self.currentPlayer = self.player1

    def alternateTurn(self):
        if self.startingPlayer is self.player1:
            self.startingPlayer = self.player2
            self.currentPlayer = self.player2
        else:
            self.startingPlayer = self.player1
            self.currentPlayer = self.player1

    def continueGame(self):
        """Resets the game board for a new round."""
        self.board.resetBoard() # Reset the board
        self.alternateTurn() # Start with the other player after a game ends
        self.gameStatus.updateGameStatus(Status.ONGOING) # Reset status to ongoing

    def resetGame(self):
        """Resets the game state, board, and players' scores."""
        self.board.resetBoard() # Clear the board
        self.player1.resetScore()
        self.player2.resetScore()
        self.startingPlayer = self.player1 # Reset to Player 1
        self.currentPlayer = self.player1 
        self.gameStatus.updateGameStatus(Status.ONGOING) # Reset status to ongoing