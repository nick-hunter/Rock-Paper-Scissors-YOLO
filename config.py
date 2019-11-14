config = {
    'classes_path': 'model/obj.names',
    'cfg_path': 'model/yolov3-three.cfg',
    'weights_path': 'model/yolov3-rps_final.weights',
    'inpWidth': 416,
    'inpHeight': 416,
    'scale': 0.00392,
    'mean': [0,0,0],
    'confThreshold': 0.45,
    'nmsThreshold': 0.01,
    'circle_scale':0.65
}

class Config:
    def __init__(self):
        self._config = config

    def get_property(self, property_name):
        if property_name not in self._config.keys():
            return None
        return self._config[property_name]

    def set_property(self, property_name, property_value):
        self._config[property_name] = property_value
