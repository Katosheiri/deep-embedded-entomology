from pynq_dpu import DpuOverlay
import numpy as np

from preprocess import *
from process import *
from inference import *

def arg_to_name(class_file, inference_result, inference_result_name):
    # Read class names
    with open(class_file, 'r') as f:
        class_names = f.read().splitlines()

    # Read inference_result_arg
    with open(inference_result, 'r') as f:
        class_numbers = f.read().splitlines()

    # Transform arg into name
    class_labels = [class_names[int(num)] for num in class_numbers]

    # Write result in txt
    with open(inference_result_name, 'w') as f:
        for label in class_labels:
            f.write(label + '\n')
            
    print("arg to name done.")


# Init
overlay = DpuOverlay("../dpu.bit")
overlay.load_model("../ultra96v2_tipu12.xmodel")

image_folder = "/path/to/image/folder"
class_file = "/path/to/class/file"
inference_result = "/path/to/output"
inference_result_name = "/path/to/output/names"

# Load class names from the class_map file
with open(class_file, "r") as file:
    class_names = [line.strip() for line in file.readlines()]

num_thread = 4

show_all_info = False
evaluate_on_thread_range = True

if evaluate_on_thread_range==True:
    for i in range(num_thread):
        predictions_list = test_accuracy(overlay, image_folder, i+1, show_all_info, class_file, inference_result)
        
else:
    predictions_list = test_accuracy(overlay, image_folder, num_thread, show_all_info, class_file, inference_result)
    
# Convert args into names
arg_to_name(class_file, inference_result, inference_result_name)