import numpy as np

def calculate_softmax(data):
    e_x = np.exp(data - np.max(data))
    return e_x / e_x.sum()

def predict_label_class(softmax, class_file):
    class_arg = np.argmax(softmax)
    return class_arg

def runDPU(runner, img, class_file, predictions_list, shapeIn, shapeOut, outputSize, inference_result):    
    n_of_images = len(img)
    count = 0
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
        predicted_label_class = predict_label_class(softmax, class_file)
        
        # To compute f1 score later on
        predictions_list.append(predicted_label_class)
            
        count += 1
        
    np.savetxt(inference_result, predictions_list, fmt='%d', delimiter=',')