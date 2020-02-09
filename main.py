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
from LabelboxUpload import LabelBoxUpload

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
    '''Application class for Kivy'''

    def build(self):
        '''Build the user interface'''
        self.title = 'Rock Paper Scissors'
        self.configuration = Config()
        self.camera = ImageProvider()
        self.process = ImageProcessor(self.camera, self.configuration)
        self.game = Game()
        self.LB = LabelBoxUpload()

        sidebar_width = 0.3
        frame_width, frame_height = self.camera.get_dimensions()
        win_width, win_height = Window.size

        # Set window size and position
        Window.left = (win_width-frame_width)/2
        Window.size = (frame_width, frame_height/(1+sidebar_width))

        # Play button
        self.play = Button(text="Play", size_hint_x=1.0, size_hint_y=0.1, font_size=50)
        self.score_label = Label(text="", size_hint_y=0.1, font_size='20sp')
        self.play.bind(on_press=self.start_game)

        # Main image and text overlay
        self.img_layout = AnchorLayout(anchor_x='left', anchor_y='center')
        self.img = Image(keep_ratio=True, allow_stretch=True, size_hint_x=1)
        self.big_text = Label(text="", font_size='75sp', markup=True)
        self.img_layout.add_widget(self.img)
        self.img_layout.add_widget(self.big_text)

        # Main layout
        self.layout = BoxLayout(orientation='horizontal')
        self.sidebar = BoxLayout(orientation='vertical', size_hint_x=sidebar_width)

        # Bottom layout to display small images
        self.plays_layout = GridLayout(cols=1, size_hint = (.5, .3), padding = (2,2), pos_hint = {'center_x':.5}) #
        self.player_img = Image(keep_ratio=True, allow_stretch=True, size_hint_x = .5, size_hint_y = 1, source=file_path("img/black.png"))
        self.wrong = Button(text="Something Wrong?", size_hint_y=.04, opacity=0)
        self.wrong.bind(on_press=self.correction)
        self.computer_img = Image(keep_ratio=True, allow_stretch=True, size_hint_x = .5, size_hint_y = 1, source=file_path("img/black.png"))
        self.player_label = Label(text="",size_hint_x=.2)
        self.computer_label = Label(text="",size_hint_x=.2)

        self.plays_layout.add_widget(self.player_img)
        self.plays_layout.add_widget(self.player_label)

        self.plays_layout.add_widget(self.computer_img)
        self.plays_layout.add_widget(self.computer_label)

        self.sidebar.add_widget(self.play)
        self.sidebar.add_widget(self.score_label)
        self.sidebar.add_widget(self.plays_layout)
        self.sidebar.add_widget(self.wrong)

        self.layout.add_widget(self.img_layout)
        self.layout.add_widget(self.sidebar)

        self.active_game = False
        self.last_frame = None
        self.last_play = None

        self.computer_score = 0
        self.player_score = 0

        Clock.schedule_interval(self.update, 1.0/33.0)
        return self.layout

    def update(self, dt):
        '''Refresh the main image display'''
        has_frame, frame = self.camera.get_frame()
        if has_frame:
            self.display_image(frame, self.img)

    def start_game(self, instance):
        '''Called to start a new game of Rock Paper Scissors'''
        wait_interval = self.configuration.get_property('wait_interval')

        labels = ["Rock", "Paper", "Scissors", "Shoot"]
        for num, label in enumerate(labels, start=1):
            Clock.schedule_once(partial(self.update_label, label),
                                num*wait_interval)

        Clock.schedule_once(self.process.start_processing, 6*wait_interval)
        Clock.schedule_once(self.detect_play, 6*wait_interval)

    def update_label(self, text, dt):
        '''Sets the large text which is displayed over the camera feed'''
        self.big_text.text = "[b]" + text + "[/b]"

    def detect_play(self, dt):
        '''Waits for a successful object detection'''
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
        '''Process gameplay after a successful detection'''
        self.big_text.text = ""
        print(predictions)

        computer_choice = self.game.next_play()

        choice = max(range(len(predictions)),
                     key=lambda index: predictions[index]['confidence'])
        player_choice = predictions[choice]['class']
        self.last_play = player_choice

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

        self.wrong.opacity = 0.5

        print("Computer chose " + computer_choice)
        self.computer_label.text = "Computer - " + computer_choice
        print("Player chose " + player_choice)
        self.player_label.text = "Player - " + player_choice

        self.game.add_round(player_choice, computer_choice)
        score = self.game.get_score()

        self.score_label.text = "Computer: " + str(score.computer) + \
                                ", Player: " + str(score.player)

    def display_image(self, img, target):
        '''Display an OpenCV image object in a Kivy image object

        Args:
            img: OpenCV image object
            target: Kivy Image object
        '''
        try:
            buf1 = cv.flip(img, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(img.shape[1], img.shape[0]),
                                      colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            target.texture = texture1  # display image from the texture
        except AttributeError:
            raise

    def correction(self, instance):
        '''Correct for an incorrect object detection by removing the last round. The
        offending image is then stored in the folder specified by corrections_path
        in config.json. If Labelbox is configured, the image is then uploaded to
        the specified dataset.
        '''
        filename = self.LB.save_pic(self.last_frame, self.last_play)
        self.LB.upload_pic(filename)

        # Remove last game
        self.game.remove_round()
        score = self.game.get_score()
        self.score_label.text = "Computer: " + str(score.computer) + \
                                ", Player: " + str(score.player)
        self.player_label.text = "Player - Unknown"


if __name__ == '__main__':
    Application().run()
