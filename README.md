# Deep Embedded Entomology

This project resulted from an internship and the collaboration between ENSEEIHT and the University San Francisco de Quito.

Our main objective was to implement AI on FPGA to study the biodiversity. This objective got refined to "deploy a fully autonomous embedded system in the jungle to classify 12 orders of insects."

## 1. Technology used

To achieve our goal, we utilized a diverse set of technologies and tools across hardware, software, and development platforms.

### Hardware

We worked with various FPGA platforms, each offering unique advantages for our AI deployment :
- **Zybo Z7**
- **Kria KV260 Vision AI Starter Kit**
- **Ultra96v2**

### Operating Systems

To manage the hardware, we employed different operating systems tailored to FPGA development:
- **PYNQ** -  A Python-based platform that simplifies FPGA programming and allows for rapid prototyping with overlays and high-level APIs.
- **Petalinux** -     A custom Linux distribution designed for embedded systems, providing control over the system's configuration and optimization for our specific use case.


### Development Platforms

We leveraged specialized development environments to design, optimize, and deploy our AI models on FPGA
:
- **Tensil** - A customizable AI acceleration platform enabling efficient execution of neural networks on embedded devices.
- **Vitis AI** - AMD's comprehensive development environment for AI inference on edge devices, offering tools for model optimization, quantization, and deployment.

### Architectures
The AI models were implemented on FPGA architectures optimized for different processing tasks :
- **TCU (Tensor Compute Unit)** - Specialized for handling tensor operations critical in deep learning workloads.
- **DPU (Deep Learning Processing Unit)** - A highly efficient architecture tailored for running AI inference on FPGAs, providing accelerated performance for deep learning tasks.

### Programming Languages
We compared the use of high-level and low-level programming to find the best solution suited for our problem :
- **Python**
- **C++**


## 2. How to navigate this repository

```create_model_tipu12``` details the flow to create our AI model, from the creation of the dataset to the training of the model.

```detection``` details how we implemented detection algorithms to crop images around insects.

```hardware``` contains the code we used on all boards.

```tensil``` details how to compile with tensil.

```vitis_ai``` details how to install and use Vitis AI.


## 3. Main results