import cv2 as cv
from threading import Thread

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
        self.play=Button(size_hint_x=1.0,size_hint_y=0.1)
        layout = GridLayout(cols=1)
        layout.add_widget(self.img)

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
            self.img.width = window_width
            self.img.height = window_height
            self.img.texture = texture1 # display image from the texture


if __name__ == '__main__':
    Application().run()
