import os
import shutil
from sklearn.model_selection import train_test_split

def split_dataset(dataset_dir, output_dir, test_size=0.2, val_size=0.1):
    # Create output directories
    train_dir = os.path.join(output_dir, 'train')
    val_dir = os.path.join(output_dir, 'val')
    test_dir = os.path.join(output_dir, 'test')

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # Iterate over each class folder
    for class_name in os.listdir(dataset_dir):
        class_dir = os.path.join(dataset_dir, class_name)
        if os.path.isdir(class_dir):
            # List all files in the class directory
            files = [os.path.join(class_dir, f) for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
            
            # Split files into training, validation, and test sets
            train_files, test_files = train_test_split(files, test_size=test_size)
            train_files, val_files = train_test_split(train_files, test_size=val_size / (1 - test_size))
            
            # Copy files to respective directories
            for f in train_files:
                class_train_dir = os.path.join(train_dir, class_name)
                os.makedirs(class_train_dir, exist_ok=True)
                shutil.copy(f, class_train_dir)
                
            for f in val_files:
                class_val_dir = os.path.join(val_dir, class_name)
                os.makedirs(class_val_dir, exist_ok=True)
                shutil.copy(f, class_val_dir)
                
            for f in test_files:
                class_test_dir = os.path.join(test_dir, class_name)
                os.makedirs(class_test_dir, exist_ok=True)
                shutil.copy(f, class_test_dir)

    print(f"Dataset split into train, val, and test sets.")
    print(f"Train directory: {train_dir}")
    print(f"Validation directory: {val_dir}")
    print(f"Test directory: {test_dir}")

# Parameters
dataset_dir = 'Path/to/cropped/folder'
output_dir = '/Path/to/output/dataset'
test_size = 0.2
val_size = 0.1

# Split dataset
split_dataset(dataset_dir, output_dir, test_size, val_size)
