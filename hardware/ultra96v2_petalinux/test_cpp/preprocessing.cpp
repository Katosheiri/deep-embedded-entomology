#include "preprocessing.h"

using namespace cv;
using namespace std;

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
