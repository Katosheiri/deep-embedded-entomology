#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <mutex>
#include <opencv2/opencv.hpp>
#include <queue>
#include <string>
#include <thread>
#include <vector>
#include <filesystem>
#include <functional>
#include <iomanip>
#include <memory>
#include <numeric>

#include "common.h"

#define IMAGE_WIDTH         224
#define IMAGE_HEIGHT        224
#define IMAGE_CHANNELS      3
#define IMAGE_TOTAL_PIXELS  (IMAGE_WIDTH * IMAGE_HEIGHT * IMAGE_CHANNELS)
#define N_CLASSES           12

GraphInfo shapes;
using namespace std;
using namespace chrono;
using namespace cv;

typedef int8_t dpu_type;

static const char* lookup(int index) {
  static const char* table[] = {
#include "../resnet50_pt/words.inc"
  };

  if (index < 0) {
    return "";
  } else {
    return table[index];
  }
};

void load_images_from_folder(const string& folder_path, int max_images, uint8_t* images, uint8_t* labels) {
    int n_images = 0;   
    // Iterate through the table lookup table of the class
    for (int i = 0; i < N_CLASSES; i++) {
        if (n_images >= max_images) {
            break;
        }
        string class_folder = folder_path + "/" + lookup(i);
        int n_images_class = 0;
        for (const auto& entry : filesystem::directory_iterator(class_folder)) {
            if (entry.is_regular_file()) {
                string image_path = entry.path();
                Mat image = imread(image_path);
                if (image.empty()) {
                    cout << "Could not read image: " << image_path << endl;
                    continue;
                }
                resize(image, image, Size(IMAGE_WIDTH, IMAGE_HEIGHT));
                memcpy(images + n_images * IMAGE_TOTAL_PIXELS, image.data, IMAGE_TOTAL_PIXELS);
                memcpy(labels + n_images, (uint8_t*)&i, sizeof(uint8_t));
                n_images++;
                n_images_class++;
            }
            if (n_images >= max_images) {
                break;
            }
        }
        cout << "Found " << n_images_class << " images for class " << lookup(i) << endl;
    }
    cout << "Found " << n_images << " images in total" << endl;
}

void preprocessImages(uint8_t* images, dpu_type* processed_image_buffer, int n_images, float scale) {
    for (int i = 0; i < n_images; i++) {
        Mat processed_image = Mat(IMAGE_HEIGHT, IMAGE_WIDTH, CV_8UC3, images + i * IMAGE_TOTAL_PIXELS);
        processed_image.convertTo(processed_image, CV_32FC3);
        cvtColor(processed_image, processed_image, COLOR_BGR2RGB);
        processed_image = processed_image / 255.0f;
        float mean[3] = {0.485f, 0.456f, 0.406f};
        float std[3] = {0.229f, 0.224f, 0.225f};
        subtract(processed_image, Scalar(mean[0], mean[1], mean[2]), processed_image);
        divide(processed_image, Scalar(std[0], std[1], std[2]), processed_image);
        processed_image.convertTo(processed_image, CV_8SC3, scale);
        memcpy(processed_image_buffer + i * IMAGE_TOTAL_PIXELS, processed_image.data, IMAGE_TOTAL_PIXELS*sizeof(dpu_type));
    }
}

static vector<float> softmax(const vector<float>& input) {
    auto output = vector<float>(input.size());
    transform(input.begin(), input.end(), output.begin(), expf);
    auto sum = accumulate(output.begin(), output.end(), 0.0f);
    transform(output.begin(), output.end(), output.begin(),
                   [sum](float v) { return v / sum; });
    return output;
}

static vector<float> int8ToFloat(const int8_t* input, int size, float scale) {
    auto output = vector<float>(size);
    for (int i = 0; i < size; i++) {
        output[i] = input[i] * scale;
    }
    return output;
}

void displayResult(int8_t* result, int n_classes) {
    vector<float> output = int8ToFloat(result, n_classes, 0.5);
    vector<float> probs = softmax(output);
    auto max_it = max_element(probs.begin(), probs.end());
    auto max_index = distance(probs.begin(), max_it);
    cout << "Predicted class: " << lookup(max_index) << " with probability: " << *max_it << endl;
}

void printAccuracyBars(const vector<float>& accuracies) {
    const char barChar = '#';
    const int maxBarLength = 50; // Longueur maximale de la barre

    for (size_t i = 0; i < accuracies.size(); ++i) {
        // Calculer la longueur de la barre proportionnellement à la précision
        int barLength = static_cast<int>(accuracies[i] * maxBarLength);
        int limit = maxBarLength - barLength - 1;

        // Afficher la barre
        cout << "Class " << setw(11) << lookup(i) << " [" << setw(5) << fixed << setprecision(2) << accuracies[i] * 100 << "%] : ";
        cout << string(barLength, barChar) << string(limit, ' ') << "|" << endl;
              
    }
}

void printAccuracy(dpu_type* outputBuffer, uint8_t* labels, int n_images, float scale) {
    vector<int> correct_classes(N_CLASSES, 0);
    int correct = 0;
    vector<float> output, probs;
    for (int i = 0; i < n_images; i++) {
        output = int8ToFloat(outputBuffer + i * N_CLASSES, N_CLASSES, scale);
        // output = vector<float>(outputBuffer + i * N_CLASSES, outputBuffer + (i + 1) * N_CLASSES);
        probs = softmax(output);
        auto max_it = max_element(probs.begin(), probs.end());
        auto max_index = distance(probs.begin(), max_it);
        // cout << "Predicted class: " << lookup(max_index) << " with probability: " << *max_it << endl;
        // cout << "Actual class:    " << lookup(labels[i]) << endl;

        if (max_index == labels[i]) {
            int class_index = labels[i];
            correct_classes[class_index]++;
            correct++;
        }
    }
    vector<float> class_accuracy(N_CLASSES, 0);
    for (int i = 0; i < N_CLASSES; i++) {
        class_accuracy[i] = (float)correct_classes[i] / count(labels, labels + n_images, i);
        // cout << "Accuracy for class " << lookup(i) << ": " << class_accuracy[i] << endl;
    }
    printAccuracyBars(class_accuracy);
    cout << "Global accuracy: " << 100.0*correct/n_images << "%" << endl;


}


void runDPU(vart::Runner* runner, dpu_type* inputBuffer, dpu_type* outputBuffer, int n_images) {
    char spinner[] = {'|', '/', '-', '\\'};
    int spinner_length = sizeof(spinner) / sizeof(spinner[0]);
    int spinner_index = 0;

    // init out data
    float mean[3] = {104, 117, 123};
    vector<unique_ptr<vart::TensorBuffer>> inputs, outputs;
    vector<vart::TensorBuffer*> inputsPtr, outputsPtr;
    
    // get in/out tensor
    auto outputTensors = cloneTensorBuffer(runner->get_output_tensors());
    auto inputTensors = cloneTensorBuffer(runner->get_input_tensors());

    // get tensor shape info
    int outHeight = shapes.outTensorList[0].height;
    int outWidth = shapes.outTensorList[0].width;
    int inHeight = shapes.inTensorList[0].height;
    int inWidth = shapes.inTensorList[0].width;

    int inSize = shapes.inTensorList[0].size;
    int outSize = shapes.outTensorList[0].size;

    dpu_type *loc_inputBuffer = inputBuffer;
    dpu_type *loc_outputBuffer = outputBuffer;

    auto start = high_resolution_clock::now();

    for (int i = 0; i < n_images; i++) {
        loc_inputBuffer = inputBuffer + i * inSize;
        loc_outputBuffer = outputBuffer + i * outSize;

        // tensor buffer prepare
        inputs.push_back(make_unique<CpuFlatTensorBuffer>(
                loc_inputBuffer, inputTensors[0].get()));
        outputs.push_back(make_unique<CpuFlatTensorBuffer>(
                loc_outputBuffer, outputTensors[0].get()));

        inputsPtr.clear();
        outputsPtr.clear();
        inputsPtr.push_back(inputs[0].get());
        outputsPtr.push_back(outputs[0].get());

        // run
        auto job_id = runner->execute_async(inputsPtr, outputsPtr);
        runner->wait(job_id.first, -1);

        // Read the output tensor
        // displayResult(loc_outputBuffer, outSize);
        
        // Clean up
        inputs.clear();
        outputs.clear();

        // if ((i % 100) == 0 && (i != 0)) {
        //     cout << "Processed " << i << " images" << endl;
        // }

        // cout << "\r" << spinner[i % spinner_length] << flush;
    }

    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<milliseconds>(stop - start);
    // cout << "DPU execution time: " << duration.count() / 1000.0 << " seconds" << endl;
    // cout << "DPU FPS: " << 1000.0*n_images / duration.count() << endl;

    cout << "All images processed" << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "Usage: " << argv[0] << " <folder_path> <n_threads>" << endl;
        cout << "Example: ./debug_data ../resnet50_mt_py/test_tipu12/ 4" << endl;
        return 1;
    }
    cout << "\n\nStart of program" << endl;
    
    string folder_path = argv[1];
    int n_thds = atoi(argv[2]);
    const int n_threads = n_thds;

    // Get the number of images in the folder
    int n_images = 0;
    for (int i = 0; i < N_CLASSES; i++) {
        string class_folder = folder_path + "/" + lookup(i);
        for (const auto& entry : filesystem::directory_iterator(class_folder)) {
            if (entry.is_regular_file()) {
                n_images++;
            }
        }

        cout << "class_folder " << class_folder << endl;
    }
    cout << "Found " << n_images << " images in subfolders" << endl;
    // if (n_images > max_images) {
    //     n_images = max_images;
    //     cout << "Limiting number of images to " << n_images << endl;
    // }

    // n_images = 2200;

    // Allocate memory for the images and labels
    uint8_t* images = new uint8_t[n_images * IMAGE_TOTAL_PIXELS];
    uint8_t* labels = new uint8_t[n_images];
    dpu_type* inputBuffer = new dpu_type[n_images * IMAGE_TOTAL_PIXELS];
    dpu_type* outputBuffer = new dpu_type[n_images * N_CLASSES];

    // Load the images and labels into the buffers
    auto load_preprocess_start = high_resolution_clock::now();
    load_images_from_folder(folder_path, n_images, images, labels);
    cout << "Images and labels loaded" << endl;

    // DPU initializations
    string xmodel_file = "/home/root/Vitis-AI/demo/VART/resnet50_mt_py/ultra96v2_tipu12.xmodel";
    auto graph = xir::Graph::deserialize(xmodel_file);
    auto subgraph = get_dpu_subgraph(graph.get());
    CHECK_EQ(subgraph.size(), 1u)
        << "Subgraph should have one and only one dpu subgraph.";
    // LOG(INFO) << "create running for subgraph: " << subgraph[0]->get_name();

    // Create runner
    auto runner0 = vart::Runner::create_runner(subgraph[0], "run");
    auto runner1 = vart::Runner::create_runner(subgraph[0], "run");
    auto runner2 = vart::Runner::create_runner(subgraph[0], "run");
    auto runner3 = vart::Runner::create_runner(subgraph[0], "run");

    // In/out tensors
    auto inputTensors = runner0->get_input_tensors();
    auto outputTensors = runner0->get_output_tensors();
    auto input_scale = get_input_scale(runner0->get_input_tensors()[0]);
    auto output_scale = get_output_scale(runner0->get_output_tensors()[0]);
    int inputCnt = inputTensors.size();
    int outputCnt = outputTensors.size();
    cout << "Input scale: " << input_scale << ". Output scale: " << output_scale << endl;

    // Get in/out tensor shape
    TensorShape inshapes[inputCnt];
    TensorShape outshapes[outputCnt];
    shapes.inTensorList = inshapes;
    shapes.outTensorList = outshapes;
    getTensorShape(runner0.get(), &shapes, inputCnt, outputCnt);
    cout << "DPUs created" << endl;

    // Preprocess the images
    preprocessImages(images, inputBuffer, n_images, input_scale);
    delete[] images;
    cout << "Images preprocessed" << endl;

    // Buffer division
    int n_images_1 = n_images / n_threads;
    int n_images_0 = n_images - (n_images_1 * (n_threads-1));
    int n_images_2 = n_images_1;
    int n_images_3 = n_images_1;

    dpu_type* inputBuffer0, *inputBuffer1, *inputBuffer2, *inputBuffer3;
    dpu_type* outputBuffer0, *outputBuffer1, *outputBuffer2, *outputBuffer3;
    
    if (n_threads >= 1) {
        inputBuffer0 = inputBuffer;
        outputBuffer0 = outputBuffer;
    }
    if (n_threads >= 2) {
        inputBuffer1 = inputBuffer + IMAGE_TOTAL_PIXELS * n_images_0;
        outputBuffer1 = outputBuffer + N_CLASSES * n_images_0;
    }
    if (n_threads >= 3) {
        inputBuffer2 = inputBuffer + IMAGE_TOTAL_PIXELS * (n_images_0 + n_images_1);
        outputBuffer2 = outputBuffer + N_CLASSES * (n_images_0 + n_images_1);
    }
    if (n_threads >= 4) {
        inputBuffer3 = inputBuffer + IMAGE_TOTAL_PIXELS * (n_images_0 + n_images_1 + n_images_2);
        outputBuffer3 = outputBuffer + N_CLASSES * (n_images_0 + n_images_1 + n_images_2);
    }

    // Create threads
    auto dpu_start = std::chrono::high_resolution_clock::now();
    thread workers[n_threads];
    for (auto i = 0; i < n_threads; i++) {
        if (i == 0)
        workers[i] = thread(runDPU, runner0.get(), ref(inputBuffer0), ref(outputBuffer0), n_images_0);
        if (i == 1)
        workers[i] = thread(runDPU, runner1.get(), ref(inputBuffer1), ref(outputBuffer1), n_images_1);
        if (i == 2)
        workers[i] = thread(runDPU, runner2.get(), ref(inputBuffer2), ref(outputBuffer2), n_images_2);
        if (i == 3)
        workers[i] = thread(runDPU, runner3.get(), ref(inputBuffer3), ref(outputBuffer3), n_images_3);
    }

    // Release thread resources.
    for (auto &w : workers) {
        if (w.joinable()) w.join();
    }

    // runDPU(runner0.get(), inputBuffer, outputBuffer, n_images);

    auto dpu_stop = high_resolution_clock::now();
    auto total_duration = duration_cast<milliseconds>(dpu_stop - load_preprocess_start);
    auto dpu_duration = duration_cast<milliseconds>(dpu_stop - dpu_start);
    cout << "Programm execution time: " << fixed << setprecision(2) << total_duration.count()/1000.0 << " seconds (" << total_duration.count()/1000.0/60.0 << " minutes)" << endl;
    cout << "Load + preprocess + DPU FPS (" << n_threads << " threads): " << fixed << setprecision(2) << 1000.0*n_images / total_duration.count() << endl;
    cout << "DPU execution time: " << fixed << setprecision(2) << dpu_duration.count()/1000.0 << " seconds (" << dpu_duration.count()/1000.0/60.0 << " minutes)" << endl;
    cout << "DPU FPS (" << n_threads << " threads): " << fixed << setprecision(2) << 1000.0*n_images / dpu_duration.count() << endl;


    printAccuracy(outputBuffer, labels, n_images, output_scale);

    cout << "End of program" << endl;

    delete[] labels;
    delete[] inputBuffer;
    delete[] outputBuffer;

    return 0;
}