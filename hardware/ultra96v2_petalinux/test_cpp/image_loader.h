#ifndef IMAGE_LOADER_H
#define IMAGE_LOADER_H

#include <opencv2/opencv.hpp>
#include <string>

void load_images_from_folder(const std::string& folder_path, int max_images, uint8_t* images, uint8_t* labels);
int count_images_in_folder(const std::string& folder_path);

#endif // IMAGE_LOADER_H