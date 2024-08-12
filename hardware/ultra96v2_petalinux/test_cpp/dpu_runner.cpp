#include "dpu_runner.h"
#include "utils.h"
#include <xir/graph/graph.hpp>
#include <vitis/ai/target_factory.hpp>
#include <vitis/ai/target_factory.hpp>

using namespace std;

std::unique_ptr<vart::Runner> initialize_dpu_runner(const string& xmodel_file) {
    auto graph = xir::Graph::deserialize(xmodel_file);
    auto subgraph = get_dpu_subgraph(graph.get());
    CHECK_EQ(subgraph.size(), 1u) << "Subgraph should have one and only one dpu subgraph.";
    return vart::Runner::create_runner(subgraph[0], "run");
}

void runDPU(vart::Runner* runner, dpu_type* inputBuffer, dpu_type* outputBuffer, int n_images) {
    char spinner[] = {'|', '/', '-', '\\'};
    int spinner_length = sizeof(spinner) / sizeof(spinner[0]);
    int spinner_index = 0;

    // Init out data
    vector<unique_ptr<vart::TensorBuffer>> inputs, outputs;
    vector<vart::TensorBuffer*> inputsPtr, outputsPtr;
    
    // Tensor buffer preparation
    for (int i = 0; i < n_images; i++) {
        auto inputBufferPtr = inputBuffer + i * shapes.inTensorList[0].size;
        auto outputBufferPtr = outputBuffer + i * shapes.outTensorList[0].size;

        inputs.push_back(make_unique<CpuFlatTensorBuffer>(inputBufferPtr, runner->get_input_tensors()[0].get()));
        outputs.push_back(make_unique<CpuFlatTensorBuffer>(outputBufferPtr, runner->get_output_tensors()[0].get()));

        inputsPtr.clear();
        outputsPtr.clear();
        inputsPtr.push_back(inputs[0].get());
        outputsPtr.push_back(outputs[0].get());

        // Run DPU
        auto job_id = runner->execute_async(inputsPtr, outputsPtr);
        runner->wait(job_id.first, -1);

        // Clean up
        inputs.clear();
        outputs.clear();
    }

    cout << "All images processed" << endl;
}
