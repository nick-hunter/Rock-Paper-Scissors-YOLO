from config import Config
from labelbox import Client
import numpy as np
import cv2
import time


class LabelBoxUpload:
    '''Interfaces with the Labelbox SDK to save and upload images.

    A Labelbox API key and dataset ID can be specified in config.json. If either
    value is None upload_pic() will print an error to the concole. Using
    Labelbox is optional.
    '''
    def __init__(self):
        self.configuration = Config()
        self.api_key = self.configuration.get_property('labelbox_key')
        self.dataset_id = self.configuration.get_property('labelbox_dataset')

        if self.api_key is not None:
            self.client = Client(self.api_key)
            if self.dataset_id is not None:
                self.dataset = self.client.get_dataset(self.dataset_id)

    def save_pic(self, img, detection=None):
        '''Save a picture to the pictures/ folder

        Returns:
            Relative filepath of saved image
        '''
        try:
            now = int(time.time())
            path = self.configuration.get_property('corrections_path')
            filename = path + "/" + detection + "-" + str(now) + ".jpg"
            cv2.imwrite(filename, img)
            return filename
        except Exception as e:
            pass

    def upload_pic(self, filename):
        '''Upload an image to Labelbox.
        Args:
            filename: relative or absolute path to an image. Labelbox currently
            supports JPG, PNG, and TIFF.
        '''
        try:
            self.client
            data_row = self.dataset.create_data_row(row_data=filename)
        except AttributeError:
            print("Couldn't upload pic. Labelbox client not initialized.")
