import json


class Config:
    '''Holds global configuration data. If availible reads from config.json,
    otherwise default values are used.'''
    def __init__(self):
        try:
            with open('config.json') as json_config:
                self._config = json.load(json_config)
        except FileNotFoundError:
            print('config.json not found. Using defaults.')
            self._config = {
                'classes_path': 'model/obj.names',
                'cfg_path': 'model/yolov3-three.cfg',
                'weights_path': 'model/yolov3-rps_final.weights',
                'inpWidth': 416,
                'inpHeight': 416,
                'scale': 0.00392,
                'mean': [0, 0, 0],
                'confThreshold': 0.5,
                'nmsThreshold': 0.4,
                'circle_scale': 0.65,
                'wait_interval': 0.5,
                'labelbox_key': None,
                'labelbox_dataset': None,
                'corrections_path': 'pictures'
            }

    def get_property(self, property_name):
        '''Get a configuration property by name.
        Returns None if key is not found'''
        return self._config.get(property_name)

    def set_property(self, property_name, property_value):
        '''Set a configuration property by name'''
        self._config[property_name] = property_value
