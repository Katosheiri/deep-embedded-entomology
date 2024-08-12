#include "image_loader.h"
#include "preprocessing.h"
#include "dpu_runner.h"
#include "utils.h"

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
    int n_images = count_images_in_folder(folder_path);
    cout << "Found " << n_images << " images in subfolders" << endl;

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
    auto runner0 = initialize_dpu_runner("/home/root/Vitis-AI/demo/VART/resnet50_mt_py/ultra96v2_tipu12.xmodel");
    cout << "DPUs created" << endl;

    // Preprocess the images
    preprocessImages(images, inputBuffer, n_images, get_input_scale(runner0->get_input_tensors()[0]));
    delete[] images;
    cout << "Images preprocessed" << endl;

    // Buffer division
    // Further processing...
    
    // Clean up
    delete[] labels;
    delete[] inputBuffer;
    delete[] outputBuffer;
    return 0;
}
