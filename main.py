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
from utils import file_path

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout

from kivy.config import Config as KivyConfig
KivyConfig.set('input', 'mouse', 'mouse,multitouch_on_demand')

kivy.require('1.11.1')


class Application(App):
    def build(self):
        self.title = 'Rock Paper Scissors'
        self.configuration = Config()
        self.camera = ImageProvider()
        self.process = ImageProcessor(self.camera, self.configuration)
        self.game = Game()

        # Play button
        self.play = Button(text="Play", size_hint_x=1.0, size_hint_y=0.1)
        self.score_label = Label(text="", size_hint_y=0.1)
        self.play.bind(on_press=self.start_game)

        # Main image and text overlay
        self.img_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.img = Image(keep_ratio=True, allow_stretch=True, size_hint_x=1)
        self.big_text = Label(text="", font_size='75sp', markup=True)
        self.img_layout.add_widget(self.img)
        self.img_layout.add_widget(self.big_text)

        # Main layout
        layout = BoxLayout(orientation='vertical')

        # Bottom layout to display small images
        self.plays_layout = GridLayout(cols=2, size_hint = (.5, .3), padding = (5,5), pos_hint = {'center_x':.5})
        self.player_img = Image(keep_ratio=True, allow_stretch=True, size_hint_x = .5, size_hint_y = 1, source=file_path("img/black.png"))
        self.computer_img = Image(keep_ratio=True, allow_stretch=True, size_hint_x = .5, size_hint_y = 1, source=file_path("img/black.png"))
        self.player_label = Label(text="",size_hint_x=.2)
        self.computer_label = Label(text="",size_hint_x=.2)

        self.plays_layout.add_widget(self.player_img)
        self.plays_layout.add_widget(self.computer_img)
        self.plays_layout.add_widget(self.player_label)
        self.plays_layout.add_widget(self.computer_label)

        layout.add_widget(self.play)
        layout.add_widget(self.score_label)
        layout.add_widget(self.img_layout)
        layout.add_widget(self.plays_layout)

        self.active_game = False
        self.last_frame = None

        self.computer_score = 0
        self.player_score = 0

        Clock.schedule_interval(self.update, 1.0/33.0)
        return layout

    def update(self, dt):
        has_frame, frame = self.camera.get_frame()
        if has_frame:
            self.display_image(frame, self.img)

    def start_game(self, instance):
        wait_interval = self.configuration.get_property('wait_interval')

        labels = ["Rock", "Paper", "Scissors", "Shoot"]
        for num, label in enumerate(labels, start=1):
            Clock.schedule_once(partial(self.update_label, label),
                                num*wait_interval)

        Clock.schedule_once(self.process.start_processing, 6*wait_interval)
        Clock.schedule_once(self.detect_play, 6*wait_interval)

    def update_label(self, text, dt):
        self.big_text.text = "[b]" + text + "[/b]"

    def detect_play(self, dt):
        object = None

        has_prediction, predictions = self.process.get_frame_predictions()
        has_frame, frame = self.process.get_frame()
        if has_prediction and predictions != []:
            self.last_frame = frame
            self.process_play(predictions)

            self.process.stop_processing()
        else:
            Clock.schedule_once(self.detect_play, 0.2)

    def process_play(self, predictions):
        self.big_text.text = ""
        print(predictions)

        computer_choice = self.game.next_play()

        choice = max(range(len(predictions)),
                     key=lambda index: predictions[index]['confidence'])
        player_choice = predictions[choice]['class']

        x = predictions[choice]['x'] - (predictions[choice]['width']//2)
        y = predictions[choice]['y'] - (predictions[choice]['height']//2)
        w = predictions[choice]['width']
        h = predictions[choice]['height']

        frame = self.last_frame[y:y+h, x:x+w]
        self.display_image(frame, self.player_img)

        if computer_choice == "Rock":
            self.computer_img.source = file_path('img/rock.png')
        elif computer_choice == "Paper":
            self.computer_img.source = file_path('img/paper.png')
        else:
            self.computer_img.source = file_path('img/scissors.png')

        print("Computer chose " + computer_choice)
        self.computer_label.text = "Computer - " + computer_choice
        print("Player chose " + player_choice)
        self.player_label.text = "Player - " + player_choice

        self.game.add_round(player_choice, computer_choice)
        score = self.game.get_score()

        self.score_label.text = "Computer: " + str(score.computer) + \
                                ", Player: " + str(score.player)

    def display_image(self, img, target):
        try:
            buf1 = cv.flip(img, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(img.shape[1], img.shape[0]),
                                      colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            target.texture = texture1  # display image from the texture
        except AttributeError:
            raise


if __name__ == '__main__':
    Application().run()
