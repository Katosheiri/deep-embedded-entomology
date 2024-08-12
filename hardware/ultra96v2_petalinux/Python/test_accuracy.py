import threading
import time
import numpy as np
import xir
import vart
import os

from preprocess import *
from process import *

def count_total_images(dataset_folder):
    total = 0
    for class_folder in os.listdir(dataset_folder):
        class_path = os.path.join(dataset_folder, class_folder)
        if os.path.isdir(class_path):
            total += len(os.listdir(class_path))
    return total

def count_directories(directory_path):
    count = 0
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            count += 1
    return count

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
    
def load_preprocess_images(class_folder, class_path, cnt, preprocessed_images0, label_names_list0, label_names, show_all_info):
    class_label = class_folder
    for image_name in os.listdir(class_path):
        image_path = os.path.join(class_path, image_name)
        # Skip non-image files (e.g., .ipynb_checkpoints)
        if not is_image_file(image_path):
            print("issue")
            continue

        # Preprocess image
        preprocessed_images0.append(preprocess_fn(cv2.imread(image_path)))
        label_names_list0.append(class_label)
        cnt[0] = cnt[0] + 1
            
    label_names.append(class_label)
    if ((cnt[0] != 0) & (show_all_info==True)):
        print("Number of preprocessed images: ", cnt[0])
    print("Load and preprocess over.")

def test_accuracy(subgraphs, image_folder, class_file, num_classes, num_thread, show_all_info):
    print("Number of threads: {} \n".format(num_thread))
    
    # Define our buffers
    all_dpu_runners = []
    for i in range(num_thread):
        all_dpu_runners.append(vart.Runner.create_runner(subgraphs[0], "run"))

    inputTensors = all_dpu_runners[0].get_input_tensors()
    outputTensors = all_dpu_runners[0].get_output_tensors()

    shapeIn = tuple(inputTensors[0].dims)
    shapeOut = tuple(outputTensors[0].dims)
    outputSize = int(outputTensors[0].get_data_size() / shapeIn[0])

    softmax = np.empty(outputSize)
    
    # Initialization
    time_inf = 0
    totaltime_preprocess = 0
    realCorrect = [0]
    cnt = [0]
    nb_images_per_class = np.zeros((num_classes,))
    class_accuracy = np.zeros((num_classes,))
    preprocessed_images0 = []
    label_names_list0 = []
    label_names = []
    predictions_list = []
    labels_list = []
    
    total_images = count_total_images(image_folder)
    
    
    time_start = time.time()
    for class_folder in os.listdir(image_folder):
        class_path = os.path.join(image_folder, class_folder)

        threadAll = []
        preprocessed_images0 = []
        label_names_list0 = []
        
        # Preprocessing
        time_start_preprocess = time.time()
        load_preprocess_images(class_folder, class_path, cnt, preprocessed_images0, label_names_list0, label_names, show_all_info)
        time_end_preprocess = time.time()
        totaltime_preprocess = totaltime_preprocess + time_end_preprocess-time_start_preprocess
        if show_all_info==True:
            print("Total time preprocess: {:.2f} seconds".format(totaltime_preprocess))



        label_arg = get_line_number(class_file, label_names_list0[0])

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
            t1 = threading.Thread(target=runDPU, args=(all_dpu_runners[i], preprocessed_images0[start[i]:end[i]], label_names_list0[start[i]:end[i]], class_file, realCorrect, class_accuracy, label_arg, nb_images_per_class, predictions_list, labels_list, show_all_info, shapeIn, shapeOut, outputSize))
            threadAll.append(t1)
        for x in threadAll:
            x.start()
        for x in threadAll:
            x.join()

        time_end_inf = time.time()
        time_inf = time_inf + time_end_inf - time_start_inf

        # Clear images, labels and threads to limit memory usage
        preprocessed_images0.clear()
        label_names_list0.clear()
        threadAll.clear()

        print("Done for class: {} \n".format(class_folder))
        
 
    time_end = time.time()
    timetotal = time_end - time_start

    del all_dpu_runners
    
    # Computes accuracy and accuracy per class
    accuracy = realCorrect[0]/total_images
    for i in range(len(class_accuracy)):
        class_accuracy[i] = class_accuracy[i]/nb_images_per_class[i]

    print("Total processed images: ", cnt[0])
    print("Correct: {}/{}".format(realCorrect[0], cnt[0]))
    print("Accuracy: {:.2f}%".format(accuracy*100))
    print("Total time: {:.2f} seconds".format(timetotal))
    print("FPS total: {:.2f}".format(total_images/timetotal))
    print("FPS during inference: {:.2f}".format(total_images/time_inf))
    print("FPS during preprocess + inference: {:.2f}".format(total_images/(time_inf+totaltime_preprocess)))
    
    return accuracy, class_accuracy, label_names, predictions_list, labels_list