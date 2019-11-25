import random
import collections
import sys

Round = collections.namedtuple('Round', 'player computer result')
Score = collections.namedtuple('Score', 'player computer')


class Game:
    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.history = []
        self.rps = ['Rock', 'Paper', 'Scissors']

    #  Determine who won using standard Rock Paper Scissors rules.
    #
    #  Return Values:
    #  0 - tie game
    #  1 - computer wins
    # -1 - player wins
    def who_wins(self, player, computer):
        if player not in self.rps or computer not in self.rps:
            raise Exception("Invalid play. Must be 'Rock', 'Paper', or " \
                             "'Scissors'.")

        # Tie game
        if player == computer:
            return 0

        # Player chose rock
        elif player == "Rock":
            if computer == "Paper":
                return 1 # Computer wins
            elif computer == "Scissors":
                return -1 # Player wins

        # Player chose paper
        elif player == "Paper":
            if computer == "Scissors":
                return 1 # Computer wins
            elif computer == "Rock":
                return -1 # Player wins

        # Player chose scissors
        elif player == "Scissors":
            if computer == "Rock":
                return 1 # Computer wins
            elif computer == "Paper":
                return -1 # Player wins

    def add_round(self, player_choice, computer_choice):
        round_result = self.who_wins(player_choice, computer_choice)
        self.history.append(Round(player=player_choice, computer=computer_choice, result=round_result))

        if round_result == 1:
            self.computer_score += 1
        elif round_result == -1:
            self.player_score += 1

    def get_score(self):
        return Score(player=self.player_score, computer=self.computer_score)

    def next_play(self):
        return random.choice(self.rps)

    def reset(self):
        self.history.clear()
