import cv2 as cv
from threading import Thread
import time
from functools import partial
import random
import numpy as np

from camera import ImageProvider
from process import ImageProcessor
from game import Game
from config import Config

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.core.window import Window

kivy.require('1.11.1')


class Application(App):
    def build(self):
        self.title = 'Rock Paper Scissors'
        self.configuration = Config()
        self.camera = ImageProvider()
        self.process = ImageProcessor(self.camera, self.configuration)
        self.game = Game()

        self.img = Image(keep_ratio=True, allow_stretch=True)
        self.play = Button(text="Play", size_hint_x=1.0, size_hint_y=0.1)
        self.score_label = Label(text="", size_hint_y=0.1)
        self.play.bind(on_press=self.start_game)
        layout = GridLayout(cols=1)
        layout.add_widget(self.play)
        layout.add_widget(self.score_label)
        layout.add_widget(self.img)

        self.active_game = False
        self.game_start = 0
        self.rps_counter = 0
        self.consume_predictions = True

        self.computer_score = 0
        self.player_score = 0

        Clock.schedule_interval(self.update, 1.0/33.0)
        return layout

    def update(self, dt):
        has_frame, frame = self.process.get_frame()
        if has_frame:
            buf1 = cv.flip(frame, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]),
                                      colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture1  # display image from the texture

            if self.consume_predictions:
                self.process.get_frame_predictions()

    def start_game(self, instance):
        wait_interval = self.configuration.get_property('wait_interval')

        labels = ["Rock", "Paper", "Scissors", "Shoot"]
        for num, label in enumerate(labels, start=1):
            Clock.schedule_once(partial(self.update_label, label),
                                num*wait_interval)

        Clock.schedule_once(self.process.start_processing, 5*wait_interval)
        Clock.schedule_once(self.detect_play, 6*wait_interval)
        Clock.schedule_once(partial(self.update_label, "Play"), 8*wait_interval)

    def update_label(self, text, dt):
        self.play.text = text

    def detect_play(self, dt):
        self.consume_predictions = False
        object = None

        has_prediction, predictions = self.process.get_frame_predictions()
        if has_prediction and predictions != []:
            self.process_play(predictions)
            self.consume_predictions = True
            self.process.stop_processing()
        else:
            Clock.schedule_once(self.detect_play, 0.2)

    def process_play(self, predictions):
        print(predictions)

        computer_choice = self.game.next_play()

        choice = max(range(len(predictions)),
                     key=lambda index: predictions[index]['confidence'])
        player_choice = predictions[choice]['class']

        print("Computer chose " + computer_choice)
        print("Player chose " + player_choice)

        self.game.add_round(player_choice, computer_choice)
        score = self.game.get_score()

        self.score_label.text = "Computer: " + str(score.computer) + \
                                ", Player: " + str(score.player)


if __name__ == '__main__':
    Application().run()
