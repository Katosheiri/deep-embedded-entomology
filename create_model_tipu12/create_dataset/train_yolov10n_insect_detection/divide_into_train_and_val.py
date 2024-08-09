import os
import shutil
import random
from pathlib import Path

def split_dataset(images_folder, labels_folder, output_base_folder, train_size=0.8):
    # Creates output folders
    train_img_folder = Path(output_base_folder) / 'train' / 'images'
    val_img_folder = Path(output_base_folder) / 'val' / 'images'
    train_lbl_folder = Path(output_base_folder) / 'train' / 'labels'
    val_lbl_folder = Path(output_base_folder) / 'val' / 'labels'

    for folder in [train_img_folder, val_img_folder, train_lbl_folder, val_lbl_folder]:
        folder.mkdir(parents=True, exist_ok=True)

    # Get images list
    image_files = list(Path(images_folder).glob('*'))
    random.shuffle(image_files)

    # Computes size of train/val
    split_index = int(len(image_files) * train_size)

    # Split dataset into train and val folders
    train_files = image_files[:split_index]
    val_files = image_files[split_index:]

    def copy_files(file_list, dest_img_folder, dest_lbl_folder):
        for file in file_list:
            file_name = file.name
            img_dest = dest_img_folder / file_name
            lbl_dest = dest_lbl_folder / (file.stem + '.txt')

            # Copy image
            shutil.copy(file, img_dest)

            # Copy label
            lbl_src = Path(labels_folder) / (file.stem + '.txt')
            if lbl_src.exists():
                shutil.copy(lbl_src, lbl_dest)
            else:
                print(f"Label file not found: {lbl_src}")

    # Copy files into the right directory
    copy_files(train_files, train_img_folder, train_lbl_folder)
    copy_files(val_files, val_img_folder, val_lbl_folder)

# Example
images_folder = '/Path/to/images/folder'
labels_folder = '/Path/to/labels/folder'
output_base_folder = '/Path/to/output'

split_dataset(images_folder, labels_folder, output_base_folder, train_size=0.8)
