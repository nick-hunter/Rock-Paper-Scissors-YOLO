# Computer Vision Rock Paper Scissors

### Requirements
* Python 3
* A webcam

### Installation
We recommend using a Python virtual environment.
```console
# Build the virtual environment
python3 -m venv rps-env

# Activate the virtual environment
source rps-env/bin/activate
```

To install Python dependancies run the following
```console
pip install -r requirements.txt
```

If Kivy fails to install, please consult platform specific install instructions here https://kivy.org/doc/stable/gettingstarted/installation.html

The application can now be started by running
```console
python main.py
```

### Configuration
Several configuration values are read in from a config.json file. If config.json does not exist default values will be used. To change any values copy config.json.example to config.json

* confThreshold: Object detection confidence threshold from 0.0 to 1.0.
* nmsThreshold: Non-maximum suppression threshold value
* wait_interval: Wait time in seconds between Rock, Paper, Scissors, Shoot
* corrections_path: Folder path to save mis-detected images in

##### Labelbox
Uploading images with misdetected gestures to Labelbox is supported. A Labelbox API key and dataset ID can be set in config.json. API keys can be generated under the Account section of your Labelbox account. Dataset IDs can be found in Labelbox URLs. Click on a dataset from the Datasets tab and then copy the string after dataset/ in the URL. For example, copy x's from https://app.labelbox.com/dataset/xxxxxxxxxxxxxxxxxxxxxxxxx
