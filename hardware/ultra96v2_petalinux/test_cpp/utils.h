#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <vector>
#include <vart/tensor_buffer.hpp>

std::string lookup(int index);
std::vector<vart::TensorBuffer*> get_dpu_subgraph(const xir::Graph* graph);

struct TensorShape {
    vart::TensorShape inTensorList;
    vart::TensorShape outTensorList;
};

extern TensorShape shapes;

#endif // UTILS_H
