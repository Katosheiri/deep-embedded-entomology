#ifndef PREPROCESSING_H
#define PREPROCESSING_H

#include <opencv2/opencv.hpp>
#include <vector>

typedef int8_t dpu_type;

void preprocessImages(uint8_t* images, dpu_type* processed_image_buffer, int n_images, float scale);

#endif // PREPROCESSING_H
