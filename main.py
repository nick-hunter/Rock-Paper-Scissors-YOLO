import cv2 as cv
from threading import Thread
import time
from functools import partial
import random
import numpy as np

from camera import ImageProvider
from process import ImageProcessor
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

        self.img=Image(keep_ratio=True, allow_stretch=True)
        self.play=Button(text="Play",size_hint_x=1.0,size_hint_y=0.1)
        self.score_label=Label(text="", size_hint_y=0.1)
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
        window_width, window_height = Window.size

        has_frame, frame = self.process.get_frame()
        if has_frame:
            buf1 = cv.flip(frame, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture1 # display image from the texture

            if self.consume_predictions:
                self.process.get_frame_predictions()

    def start_game(self, instance):
        wait_interval = self.configuration.get_property('wait_interval')

        labels = ["Rock", "Paper", "Scissors", "Shoot"]
        for num, label in enumerate(labels, start=1):
            Clock.schedule_once(partial(self.update_label, label), num*wait_interval)

        Clock.schedule_once(self.process.start_processing, 5*wait_interval)
        Clock.schedule_once(self.detect_play, 6*wait_interval)
        Clock.schedule_once(partial(self.update_label, "Play"), 4.0)

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
        rps = ['Rock', 'Paper', 'Scissors']
        computer_choice = random.choice(rps)
        print(predictions)

        choice = max(range(len(predictions)), key=lambda index: predictions[index]['confidence'])
        player_choice = predictions[choice]['class']

        print("Computer chose " + computer_choice)
        print("Player chose " + player_choice)

        if player_choice == computer_choice:
            print("Tie Game")

        elif player_choice == "Rock":
            if computer_choice == "Paper":
                self.computer_score += 1
            elif computer_choice == "Scissors":
                self.player_score += 1

        elif player_choice == "Paper":
            if computer_choice == "Scissors":
                self.computer_score += 1
            elif computer_choice == "Rock":
                self.player_score += 1

        elif player_choice == "Scissors":
            if computer_choice == "Rock":
                self.computer_score += 1
            elif computer_choice == "Paper":
                self.player_score += 1

        self.score_label.text = "Computer: " + str(self.computer_score) + ", Player: " + str(self.player_score)


if __name__ == '__main__':
    Application().run()
