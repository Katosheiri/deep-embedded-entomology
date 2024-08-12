#include "image_loader.h"
#include "utils.h"
#include <iostream>
#include <filesystem>

using namespace std;
using namespace cv;

void load_images_from_folder(const string& folder_path, int max_images, uint8_t* images, uint8_t* labels) {
    int n_images = 0;   
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

int count_images_in_folder(const string& folder_path) {
    int n_images = 0;
    for (int i = 0; i < N_CLASSES; i++) {
        string class_folder = folder_path + "/" + lookup(i);
        for (const auto& entry : filesystem::directory_iterator(class_folder)) {
            if (entry.is_regular_file()) {
                n_images++;
            }
        }
    }
    return n_images;
}
