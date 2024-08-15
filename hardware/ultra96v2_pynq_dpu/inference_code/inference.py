import os
import time
import threading
import cv2

from preprocess import *
from process import *

def count_total_images(dataset_folder):
    total = 0
    for class_folder in os.listdir(dataset_folder):
        class_path = os.path.join(dataset_folder, class_folder)
        if os.path.isdir(class_path):
            total += len(os.listdir(class_path))
    return total

def is_image_file(file_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(file_path)[-1].lower()
    return ext in valid_extensions

def get_line_number(class_file, class_name):
    with open(class_file, 'r') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            if line.strip() == class_name:
                return idx

    return -1 
    
def load_preprocess_images(image_folder, cnt, preprocessed_images0, show_all_info):
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        # Skip non-image files (e.g., .ipynb_checkpoints)
        if not is_image_file(image_path):
            print("issue")
            continue

        # Preprocess image
        preprocessed_images0.append(preprocess_fn(cv2.imread(image_path), image_path))
        cnt[0] = cnt[0] + 1
            
    print("Load and preprocess over.")
      
        
def test_accuracy(overlay, image_folder, num_thread, show_all_info, class_file, inference_result):
    print(f"Number of threads: {num_thread} \n")
    
    # Define our buffers
    all_dpu_runners = []
    for i in range(num_thread):
        all_dpu_runners.append(overlay.runner)

    inputTensors = all_dpu_runners[0].get_input_tensors()
    outputTensors = all_dpu_runners[0].get_output_tensors()

    shapeIn = tuple(inputTensors[0].dims)
    shapeOut = tuple(outputTensors[0].dims)
    outputSize = int(outputTensors[0].get_data_size() / shapeIn[0])
    
    # Initialization
    time_inf = 0
    totaltime_preprocess = 0
    cnt = [0]
    preprocessed_images0 = []
    predictions_list = []
    
    time_start = time.time()

    threadAll = []
    preprocessed_images0 = []

    # Preprocessing
    time_start_preprocess = time.time()
    load_preprocess_images(image_folder, cnt, preprocessed_images0, show_all_info)
    time_end_preprocess = time.time()
    totaltime_preprocess = totaltime_preprocess + time_end_preprocess-time_start_preprocess
    if show_all_info==True:
        print(f"Total time preprocess: {totaltime_preprocess:.2f} seconds")

    # Define number of images to send to threads
    if num_thread == 1:
        start = [0]
        end = [len(preprocessed_images0)]

    elif num_thread == 2:
        if len(preprocessed_images0)%2 == 0:
            start = [0, int(len(preprocessed_images0)/2)]
            end = [int(len(preprocessed_images0)/2), len(preprocessed_images0)]
        else:
            start = [0, int(len(preprocessed_images0)/2)+1]
            end = [int(len(preprocessed_images0)/2)+1, len(preprocessed_images0)]

    elif num_thread == 3:
        if len(preprocessed_images0)%3 == 0:
            start = [0, int(len(preprocessed_images0)/3), 2*int(len(preprocessed_images0)/3)]
            end = [int(len(preprocessed_images0)/3), 2*int(len(preprocessed_images0)/3), len(preprocessed_images0)]
        elif len(preprocessed_images0)%3 == 1:
            start = [0, int(len(preprocessed_images0)/3)+1, 2*int(len(preprocessed_images0)/3)]
            end = [int(len(preprocessed_images0)/3)+1, 2*int(len(preprocessed_images0)/3), len(preprocessed_images0)]
        elif len(preprocessed_images0)%3 == 2:
            start = [0, int(len(preprocessed_images0)/3)+1, 2*int(len(preprocessed_images0)/3)+1]
            end = [int(len(preprocessed_images0)/3)+1, 2*int(len(preprocessed_images0)/3)+1, len(preprocessed_images0)]

    elif num_thread == 4:
        if len(preprocessed_images0)%4 == 0:
            start = [0, int(len(preprocessed_images0)/4), 2*int(len(preprocessed_images0)/4), 3*int(len(preprocessed_images0)/4)]
            end = [int(len(preprocessed_images0)/4), 2*int(len(preprocessed_images0)/4), 3*int(len(preprocessed_images0)/4), len(preprocessed_images0)]
        elif len(preprocessed_images0)%4 == 1:
            start = [0, int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4), 3*int(len(preprocessed_images0)/4)]
            end = [int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4), 3*int(len(preprocessed_images0)/4), len(preprocessed_images0)]
        elif len(preprocessed_images0)%4 == 2:
            start = [0, int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4)+1, 3*int(len(preprocessed_images0)/4)]
            end = [int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4)+1, 3*int(len(preprocessed_images0)/4), len(preprocessed_images0)]
        elif len(preprocessed_images0)%4 == 3:
            start = [0, int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4)+1, 3*int(len(preprocessed_images0)/4)+1]
            end = [int(len(preprocessed_images0)/4)+1, 2*int(len(preprocessed_images0)/4)+1, 3*int(len(preprocessed_images0)/4)+1, len(preprocessed_images0)]


    time_start_inf = time.time()

    # Create and start threads
    for i in range(num_thread):
        t1 = threading.Thread(target=runDPU, args=(all_dpu_runners[i], preprocessed_images0[start[i]:end[i]], class_file, predictions_list, shapeIn, shapeOut, outputSize, inference_result))
        threadAll.append(t1)
    for x in threadAll:
        x.start()
    for x in threadAll:
        x.join()

    time_end_inf = time.time()
    time_inf = time_inf + time_end_inf - time_start_inf

    # Clear images, labels and threads to limit memory usage
    preprocessed_images0.clear()
    threadAll.clear()

    print(f"Inference Done. \n")

    time_end = time.time()
    timetotal = time_end - time_start

    del all_dpu_runners

    print("Total processed images: ", cnt[0])
    print(f"Total time: {timetotal:.2f} seconds")
    print(f"FPS total: {cnt[0]/timetotal:.2f}")
    print(f"FPS during inference: {cnt[0]/time_inf:.2f}")
    print(f"FPS during preprocess + inference: {cnt[0]/(time_inf+totaltime_preprocess):.2f}")
    
    return predictions_list