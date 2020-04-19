#!/usr/bin/python3

import json
import sys
import os
import re
import requests
import time
from PIL import Image
import random


data_dir = '/home/nick/Desktop/darknet_fork/darknet/data/rps'
rate_limit = True
sleep_time = .2

skip_string = 'skip_reasons'
skip_classes = {'skip_reasons', 'Rock to Paper', 'Rock to Scissors'}

# Should have one argument passed
if len(sys.argv) != 2:
    print('Please pass a filepath.')
    exit()

import_path = sys.argv[1]

# Check if the file exists
if os.path.exists(import_path):
    print('Reading data from', str(sys.argv[1]))

    # Open the file
    with open(import_path) as json_file:
        data = json.load(json_file)
else:
    print('Unable to find file')
    exit(0)

unique_names = []
for row in data:
    if row['Label'] != 'Skip':
        for key in row['Label'].keys():
            if key not in unique_names and key not in skip_classes:
                unique_names.append(key)

print('Found classes', unique_names)

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

if not os.path.exists(data_dir + '/img'):
    os.makedirs(data_dir + '/img')

# Write class file
class_file = open(data_dir + '/obj.names', 'a')
class_file.seek(0)
class_file.truncate()
for label in unique_names:
    if label != skip_string:
        class_file.write(label + '\n')
class_file.close()

validate_data = open(data_dir + '/validation.txt', 'a')
validate_data.seek(0)
validate_data.truncate()

rows_validate = 0
rows_test = 0
rows_skipped = 0

# Select only data from Validation dataset
for row in data:
    if (row['Label'] != 'Skip') and (row['Dataset Name'] == "Validation"):
        if skip_classes.isdisjoint(row['Label']):
            m = re.search('^.*\.([a-zA-Z]+)$', row['External ID'])

            print(row['ID'])

            # Does the file already exist?
            path = data_dir + '/img/' + row['ID'] + '.' + m.group(1)
            row_output = path + ' '
            if not os.path.exists(path):
                # If the file doesn't exist try to download it
                r = requests.get(row['Labeled Data'])

                if r.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(r.content)
                else:
                    print('Failed to download ' + row['ID'])
                    break

                if rate_limit:
                    time.sleep(sleep_time)

            # Get the image dimensions
            im = Image.open(path)
            width, height = im.size
            im.close()

            # Create a new file to hold annotation data
            annotation_file = open(data_dir + '/img/' + row['ID'] + '.txt', 'a')

            # Clear the file if it already exists
            annotation_file.seek(0)
            annotation_file.truncate()

            # Add each label to the annotation file
            for label,value in row['Label'].items():
                for geometry in value:
                    x_seq = [point['x'] for point in geometry['geometry']]
                    x_min, x_max = min(x_seq), max(x_seq)

                    y_seq = [point['y'] for point in geometry['geometry']]
                    y_min, y_max = min(y_seq), max(y_seq)

                    x_center = (((x_max - x_min)/2) + x_min)/width
                    y_center = (((y_max - y_min)/2) + y_min)/height

                    box_width = (x_max - x_min)/width
                    box_height = (y_max - y_min)/height

                    annotation_file.write(str(unique_names.index(label)) + ' ' + '%.8f'%x_center + ' ' + '%.8f'%y_center + ' ' + '%.8f'%box_width + ' ' + '%.8f'%box_height + '\n')
                    print(unique_names.index(label), '%.8f'%x_center, '%.8f'%y_center, '%.8f'%box_width, '%.8f'%box_height)

            annotation_file.close()

            validate_data.write(path + '\n')
            rows_validate += 1

        else:
            rows_skipped += 1
            print('Skip')
    else:
        rows_skipped += 1

validate_data.close()

print(rows_validate, ' validation')
