# YOLOv3 Training

Training a YOLO model for Rock Paper Scissors application is no different than with any other custom dataset using darknet. First, I would recommend reading [this](https://github.com/AlexeyAB/darknet#how-to-train-to-detect-your-custom-objects) page from a popular darknet fork.

If you're using Labelbox to annotate your dataset, our preprocessing scripts may be of use. The scripts assume you have at least two datasets in Labelbox. One dataset should be called Validation, to keep some images out of the training process. Rectangles should be used for annotation, with class names of Rock, Paper, and Scissors. Finally, the Labelbox project should be exported as a JSON file. Image masks are not required.

This exported JSON file can then be used with labelbox_preprocess/preprocess.py. Most importantly with this script and with labelbox_preprocess/validate.py (which is used for validation data) is to update the data_dir variable at the top of each file. These paths should point to your darknet data directory.

The script can then be ran with the Labelbox export file. For example:
```shell
python preprocess.py export-2020-04-05T18_16_59.661Z.json
```

This script will download each image in the dataset from the cloud which is not already present locally. A darknet compliant text file will be written with the same prefix as each image. These text files contain all object class and bounding box information.

preprocess.py will also write out a train.txt file and a test.txt file. Each contains file paths for images in the training or testing set respectively. By default, a random 20% of the images will be used for testing. Since a fixed random seed is not used here, running these scripts multiple times will result in different train/test splits.

# Keras LSTM Prediction

The dataset for prediction training can be found [here](https://justincollier.com/wp-content/uploads/2016/05/Rock_Paper_Scissors_Raw.xlsx). Download the excel file and then export the table to a CSV file named roshambo.csv in the prediction directory.

prediction/train.py will train several models with a varying number of LSTM units. prediction/test.py will then test the models after training. These scripts do use a fixed random seed, so as long as the dataset stays consistent, the train/test splits will remain the same. 
