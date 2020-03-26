import cv2 as cv
import sys
from process import ImageProcessor
from config import Config
import pytest

# Fake ImageProvider class to test ImageProcessor class
class ImageProvider:
    def __init__(self):
        self.test_image = cv.imread('tests/test.jpg',1)

    def get_frame(self):
        return (True, self.test_image)

    def get_dimensions(self):
        print(self.test_image.shape)
        return self.test_image.shape[:-1]

    def clear_frames(self):
        pass

def test_image_provider():
    img_provider = ImageProvider()
    config = Config()

    img_processor = ImageProcessor(img_provider, config)
    img_processor.start_processing()

    ret = False
    while not ret:
        # Get one frame
        ret, img = img_processor.get_frame()

    # Get accompanied predictions
    ret, predictions = img_processor.get_frame_predictions()

    assert predictions[0]['class'] == 'Scissors',"Test failed"

    # Stop network processing
    img_processor.stop_processing()
