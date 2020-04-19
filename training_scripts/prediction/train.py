from numpy import array
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Activation, Dropout, Dense
from keras.layers import Flatten, LSTM
from keras.layers import GlobalMaxPooling1D
from keras.models import Model
from keras.layers.embeddings import Embedding
from keras.preprocessing.text import Tokenizer
from keras.layers import Input
from keras.layers.merge import Concatenate
from keras.layers import Bidirectional
import keras
import numpy as np
from numpy import genfromtxt
import csv
import pandas as pd
from sklearn.model_selection import train_test_split

train_split = 0.9
lstm_unit_list = [1,3,5,10,20,50,100]

file_name = "roshambo.csv"

def who_wins(player1, player2):
    result = player1 - player2
    if result == 0:
        return 1 # Tie
    if result in (1,-2):
        return 2 # Player1 wins
    return 0 # Player2 wins

def reshape_roshambo(data, player=0):
    result = []
    output = []
    game = []

    for group_name, df_group in data:
        game = []
        for row_index, row in df_group.iterrows():
            moves = []
            if player == 0:
                player1 = row['player_one_throw']
                player2 = row['player_two_throw']
                if player1 != 0 and player2 != 0:
                    moves.append([player1-1, who_wins(player1,player2)])
            else:
                player1 = row['player_two_throw']
                player2 = row['player_one_throw']
                if player1 != 0 and player2 != 0:
                    moves.append([player1-1, player2-1])

            if len(moves) > 0:
                game.append(moves)
            moves = []

            if len(game) > 2:
                result.append(game[:-1])
                output.append(game[-1][0][player])

    return (np.array(result),np.array(output))

data = pd.read_csv(file_name)
data_grouped = data.groupby('game_id')

print(data['game_id'].nunique())

X, y = reshape_roshambo(data_grouped)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1, random_state=42)

def train_model(lstm_units):
    model = Sequential()
    model.add(keras.layers.Dense(9, activation='relu', input_shape=(None, 6),dtype='float32'))
    model.add(keras.layers.LSTM(lstm_units, return_sequences=False))
    model.add(keras.layers.Dense(9, activation='tanh'))
    model.add(keras.layers.Dense(3, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy')

    print(model.summary())

    for i in range(len(X_train)):
            X_, y_ = X_train[i], y_train[i]
            X_ = keras.utils.to_categorical(X_, 3)
            X_ = X_.reshape(1, X_.shape[0], 6)

            y_ = keras.utils.to_categorical(y_, 3)
            y_ = y_.reshape(1, 3)

            verbose = 2 if (i % 100 == 0) else 0
            model.fit(X_, y_, epochs=1, shuffle=False, batch_size=1, verbose=verbose)
            if verbose:
                print(i/len(X_train))

    model.save("RPS-" + str(lstm_units) + ".h5")

for units in lstm_unit_list:
    train_model(units)
