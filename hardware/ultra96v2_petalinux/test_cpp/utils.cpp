#include "utils.h"
#include <map>

using namespace std;

static map<int, string> class_map = {
    {0, "class0"},
    {1, "class1"},
    {2, "class2"},
    // Add more mappings...
};

string lookup(int index) {
    return class_map[index];
}

std::vector<vart::TensorBuffer*> get_dpu_subgraph(const xir::Graph* graph) {
    return xir::Subgraph::get_leaf_subgraphs(graph)[0]->get_op("dpu")->
}

TensorShape shapes;

void set_tensor_shapes(vart::Runner* runner) {
    shapes.inTensorList = runner->get_input_tensors();
    shapes.outTensorList = runner->get_output_tensors();
}
