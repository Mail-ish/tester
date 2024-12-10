from Game_Logic import GameLogic, Status
from Player import Player, Cross, Circle
from UI import TicTacToeGUI

class Controller:
    def __init__(self):
        # Initialize players
        self.player1 = Player(Cross())
        self.player2 = Player(Circle())
        
        # Initialize game logic
        self.game_logic = GameLogic(self.player1, self.player2)
        
        # Initialize GUI
        self.gui = TicTacToeGUI()
        self.gui.set_controller(self)

    def continueGame(self):
        """Starts a new game round while keeping scores intact."""
        self.game_logic.continueGame()  # Reset the board but keep scores
        self.gui.reset_game()           # Reset the UI
        self.game_logic.gameStatus.updateGameStatus(Status.ONGOING)  # Set game status to ongoing
        self.gui.update_player_info(self.player1, self.player2, self.game_logic.currentPlayer)

    def quitGame(self):
        """Exits the application."""
        self.gui.quit_game()

    def resetGame(self):
        """Resets the entire game, including the board, scores, and UI."""
        # Reset the game board in the logic
        self.game_logic.resetGame()

        # Reset player scores to zero
        self.player1.score.resetPlayerScore()
        self.player2.score.resetPlayerScore()

        # Reset the UI
        self.gui.reset_game()

        # Update the player info in the UI with the reset scores
        self.gui.update_player_info(self.player1, self.player2, self.player1)  # Start with Player 1

    def handle_move(self, row, col):
        """Handles a move made by the current player."""
        if self.game_logic.board.isCellEmpty(row, col):
            mark = self.game_logic.currentPlayer.getMark()
            self.game_logic.validateMove(row, col)
            self.gui.update_board(row, col, mark)
            
            if self.game_logic.gameStatus.status == Status.WIN:
                self.gui.display_winner(self.game_logic.currentPlayer)
            elif self.game_logic.gameStatus.status == Status.TIE:
                self.gui.display_tie()
            else:
                self.switchTurn()
        else:
            self.gui.display_invalid_move()

    def switchTurn(self):
        """Switches the turn to the other player."""
        self.game_logic.switchTurn()
        self.gui.update_turn(self.game_logic.currentPlayer)

    def updateGameStatus(self):
        """Checks and updates the game's status."""
        if self.game_logic.board.checkWinCondition():
            self.game_logic.gameStatus.updateGameStatus(Status.WIN)
        elif self.game_logic.board.checkTieCondition():
            self.game_logic.gameStatus.updateGameStatus(Status.TIE)
        else:
            self.game_logic.gameStatus.updateGameStatus(Status.ONGOING)

    def checkWinCondition(self):
        """Checks if the current player has won."""
        return self.game_logic.board.checkWinCondition()

    def checkTieCondition(self):
        """Checks if the game is a tie."""
        return self.game_logic.board.checkTieCondition()

    def run(self):
        """Runs the GUI loop."""
        self.gui.run()