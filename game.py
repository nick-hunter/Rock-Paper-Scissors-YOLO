import random
import collections
import sys

# Named tuple to hold game rounds
Round = collections.namedtuple('Round', 'player computer result')

# Named tuple to hold score
Score = collections.namedtuple('Score', 'player computer')


class Game:
    '''The game class stores gameplay history, determines who won a round,
    and chooses the next computer play. It also allows for the removal of the
    last game if a detection is incorrect.
    '''
    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.history = []
        self.rps = ['Rock', 'Paper', 'Scissors']

    def who_wins(self, player, computer):
        '''Determine who won using standard Rock Paper Scissors rules.

        Args:
            player, computer - 'Rock', 'Paper', or 'Scissors'

        Returns:
             0 - tie game
             1 - computer wins
            -1 - player wins
        '''
        if player not in self.rps or computer not in self.rps:
            raise Exception("Invalid play. Must be 'Rock', 'Paper', or " \
                             "'Scissors'.")
        rps = {
            'Rock': 1,
            'Paper': 2,
            'Scissors': 3
        }
        result = rps[player] - rps[computer]
        if result == 0:
            return 0 # Tie
        if result in (1,-2):
            return -1 # Player wins
        return 1 # Computer wins

    def add_round(self, player_choice, computer_choice):
        '''Add a game round to the history

        Args:
            player_choice, computer_choice - 'Rock', 'Paper', or 'Scissors'
        '''
        round_result = self.who_wins(player_choice, computer_choice)
        self.history.append(Round(player=player_choice, computer=computer_choice, result=round_result))

        if round_result == 1:
            self.computer_score += 1
        elif round_result == -1:
            self.player_score += 1

    def remove_round(self):
        '''Remove the last round from history and recalculate score'''
        if len(self.history) > 0:
            self.history.pop()

            self.computer_score = 0
            self.player_score = 0

            for game in self.history:
                if game.result == 1:
                    self.computer_score += 1
                elif game.result == -1:
                    self.player_score += 1

    def get_score(self):
        '''Returns a Score named tuple with the current score'''
        return Score(player=self.player_score, computer=self.computer_score)

    def next_play(self):
        '''Pick the next computer play'''
        return random.choice(self.rps)

    def reset(self):
        '''Reset the score'''
        self.computer_score = 0
        self.player_score = 0
        self.history.clear()
