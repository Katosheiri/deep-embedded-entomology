import numpy as np
import xir
import vart

def calculate_softmax(data):
    e_x = np.exp(data - np.max(data))
    return e_x / e_x.sum()

def predict_label_name(class_file, softmax):
    with open(class_file, "r") as f:
        lines = f.readlines()
        lines = [item.strip() for item in lines]
        class_arg = np.argmax(softmax)
        class_name = lines[class_arg]
    return class_name

def predict_label_arg(softmax):
    class_arg = np.argmax(softmax)
    return class_arg

def runDPU(runner, img, labels, class_file, realCorrect, class_accuracy, label_arg, nb_images_per_class, predictions_list, labels_list, show_all_info, shapeIn, shapeOut, outputSize):
    n_of_images = len(img)
    count = 0
    correct = 0
    while count < n_of_images:
        inputData = [np.empty(shapeIn, dtype=np.float32, order="C")]
        outputData = [np.empty(shapeOut, dtype=np.float32, order="C")]

        imageRun = inputData[0]
        imageRun[0, ...] = img[count % n_of_images].reshape(shapeIn[1:])

        job_id = runner.execute_async(inputData, outputData)
        runner.wait(job_id)
        
        # Process output and calculate softmax
        temp = [j.reshape(1, outputSize) for j in outputData]
        softmax = calculate_softmax(temp[0][0])
        predicted_label_name = predict_label_name(class_file, softmax)
        
        # To compute f1 score later on
        predictions_list.append(predicted_label_name)
        labels_list.append(labels[0])
        
        if predicted_label_name == labels[0]:
            correct += 1
            class_accuracy[label_arg] += 1
            
        count += 1
        
    nb_images_per_class[label_arg] = nb_images_per_class[label_arg] + n_of_images
    class_accuracy[label_arg] = class_accuracy[label_arg]
    realCorrect[0] = realCorrect[0] + correct
    if show_all_info==True:
        print("Correct : ", realCorrect[0])