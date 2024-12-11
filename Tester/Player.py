class Mark:
    def __init__(self, mark_type: str, current_row: int = -1, current_col: int = -1):
        self.type = mark_type  #"CROSS" or "CIRCLE"

class Cross(Mark):
    #represents a CROSS mark.
    def __init__(self):
        super().__init__("X")


class Circle(Mark):
    #represents a CIRCLE mark.
    def __init__(self):
        super().__init__("O")


class Score:
    #represents the score of a player.
    def __init__(self):
        self.win_count = 0
        self.tie_count = 0

    def incrementWin(self):
        # increments the win count
        self.win_count += 1

    def incrementTie(self):
        #increments the tie count
        self.tie_count += 1

    def resetPlayerScore(self):
        self.win_count = 0
        self.tie_count = 0

class Player:
    def __init__(self, mark: Mark):
       #initialize the player
        self.mark = mark
        self.score = Score()

    def getMark(self) -> str:
        # Returns the type of mark the player is using.
        return self.mark.type

    def addWin(self):
        #Increments the player's win count.
        self.score.incrementWin()

    def addTie(self):
        #Increments the player's tie count.
        self.score.incrementTie()

    def resetScore(self):
        self.score.resetPlayerScore()

    def getScore(self):
         #Returns the player's current score.
        return {"wins": self.score.win_count, "ties": self.score.tie_count}
