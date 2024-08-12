#ifndef DPU_RUNNER_H
#define DPU_RUNNER_H

#include <vart/runner.hpp>
#include <memory>
#include <string>

std::unique_ptr<vart::Runner> initialize_dpu_runner(const std::string& xmodel_file);
void runDPU(vart::Runner* runner, dpu_type* inputBuffer, dpu_type* outputBuffer, int n_images);

#endif // DPU_RUNNER_H
