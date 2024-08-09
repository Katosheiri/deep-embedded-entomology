import os
import json
import shutil
from pathlib import Path
from PIL import Image

def convert_json_to_yolo(json_file, img_width, img_height):
    class_mapping = {
        'Araneae': 0,
        'Coleoptera': 1,
        'Diptera': 2,
        'Hemiptera': 3,
        'Hymenoptera': 4,
        'Lepidoptera': 5,
        'Odonata': 6
    }
    
    with open(json_file, 'r') as f:
        data = json.load(f)

    img_name = data['asset']['name']
    output_txt_lines = []

    for region in data['regions']:
        class_name = region['tags'][0]
        if class_name not in class_mapping:
            continue

        class_id = class_mapping[class_name]
        bbox = region['boundingBox']

        x_center = (bbox['left'] + bbox['width'] / 2) / img_width
        y_center = (bbox['top'] + bbox['height'] / 2) / img_height
        width = bbox['width'] / img_width
        height = bbox['height'] / img_height

        output_txt_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")

    return output_txt_lines

def copy_images_and_json(json_folder, image_folder, output_image_folder, output_json_folder):
    if not os.path.exists(output_image_folder):
        os.makedirs(output_image_folder)
    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)

    json_files = Path(json_folder).glob('*.json')

    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)

        img_name = data['asset']['name']
        img_path = Path(image_folder) / img_name

        # Define paths for the output directories
        output_img_path = Path(output_image_folder) / img_name
        txt_file_name = Path(img_name).stem + '.txt'
        output_txt_path = Path(output_txt_folder) / txt_file_name

        if img_path.exists():
            print(f"Copying image {img_name} to {output_image_folder}")
            img = Image.open(img_path)
            img_width, img_height = img.size
            shutil.copy(img_path, output_img_path)
        else:
            print(f"Image file not found: {img_path}")

        print(f"Creating TXT file {txt_file_name} in {output_txt_folder}")
        converted_txt = convert_json_to_yolo(json_file, img_width, img_height)
        with open(output_txt_path, 'w') as txt_file:
            txt_file.write('\n'.join(converted_txt))

# Example
data_dir = '/Path/to/dataset/directory'
output_image_folder = '/Path/to/output/images/folder'
output_txt_folder = '/Path/to/output/labels/folder'

for root, dirs, files in os.walk(data_dir):
    for dir in dirs:
        image_folder = os.path.join(root, dir)
        json_folder = os.path.join(image_folder, 'annotations')
        print(f"Found directory: {image_folder}")
        copy_images_and_json(json_folder, image_folder, output_image_folder, output_txt_folder)
