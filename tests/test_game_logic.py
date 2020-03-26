import pytest
from game import Game

game_test = Game()
rps = ['Rock', 'Paper', 'Scissors']

def test_winner():
    assert game_test.who_wins('Rock', 'Rock') == 0
    assert game_test.who_wins('Paper', 'Scissors') == 1
    assert game_test.who_wins('Scissors', 'Paper') == -1

def test_score():
    game_test.add_round('Rock', 'Scissors')
    game_test.add_round('Paper', 'Rock')
    game_test.add_round('Paper', 'Scissors')

    assert game_test.get_score() == (2,1)

def test_remove_round():
    game_test.remove_round()
    assert game_test.get_score() == (2,0)

def test_predict():
    assert game_test.next_play() in rps
    assert game_test.next_play() in rps
    assert game_test.next_play() in rps

def test_reset():
    game_test.reset()
    assert game_test.get_score() == (0,0)
