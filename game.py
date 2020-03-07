import random
import collections
import sys
import numpy as np
from numpy.random import choice
import keras
from keras.models import Sequential
from keras.layers.core import Activation, Dropout, Dense
from keras.layers import Flatten, LSTM
from keras.layers import Input
from utils import file_path

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
        self.model_input = []
        self.prediction_history = []
        self.rps = ['Rock', 'Paper', 'Scissors']
        self.initial_probability_distribution = [0.35, 0.33, 0.32]
        self.load_model()

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
        input_mapping = {
            'Rock': 0,
            'Paper': 1,
            'Scissors': 2
        }

        # For the prediction model, all inputs are from 0-2
        network_result_mapping = {
             0: 1,
            -1: 2,
             1: 0
        }

        round_result = self.who_wins(player_choice, computer_choice)
        self.history.append(Round(player=player_choice, computer=computer_choice, result=round_result))
        self.model_input.append([input_mapping[player_choice], network_result_mapping[round_result]])

        if round_result == 1:
            self.computer_score += 1
        elif round_result == -1:
            self.player_score += 1

        print(self.calculate_prediction_accuracy())

    def remove_round(self):
        '''Remove the last round from history and recalculate score'''
        if len(self.history) > 0:
            self.history.pop()
            self.prediction_history.pop()

            self.computer_score = 0
            self.player_score = 0

            # Recalculate the score
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
        win_against = {
            'Rock': 'Paper',
            'Paper': 'Scissors',
            'Scissors': 'Rock'
        }
        
        if len(self.model_input) >  0:
            X_ = keras.utils.to_categorical(self.model_input, 3)
            X_ = X_.reshape(1, X_.shape[0], 6)
            prediction = self.model.predict(X_,batch_size=1)
            self.prediction_history.append(self.rps[np.argmax(prediction)])
            return win_against[self.rps[np.argmax(prediction)]]
        else:
            prediction = choice(self.rps, 1, p=self.initial_probability_distribution)[0]
            self.prediction_history.append(prediction)
            return win_against[prediction]

    def calculate_prediction_accuracy(self):
        ''' Returns the percentage of rounds predicted correctly '''
        rounds = len(self.history)
        correct = 0
        for i in range(len(self.history)):
            if self.history[i].player == self.prediction_history[i]:
                correct += 1
        return correct/rounds

    def reset(self):
        '''Reset the score'''
        self.computer_score = 0
        self.player_score = 0
        self.history.clear()
        self.model_input.clear()

    def load_model(self):
        ''' Load the Keras prediction model '''
        self.model = Sequential()
        self.model.add(keras.layers.Dense(9, activation='relu', input_shape=(None, 6),dtype='float32'))
        self.model.add(keras.layers.LSTM(50, return_sequences=False))
        self.model.add(keras.layers.Dense(9, activation='tanh'))
        self.model.add(keras.layers.Dense(3, activation='softmax'))
        self.model.compile(optimizer='adam', loss='categorical_crossentropy')
        self.model.load_weights(file_path("model/RPS-50.h5"))
