#!/bin/bash

# Copyright © 2023 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

echo "Activate environment..."
# conda activate color_cls

DATA_DIR=./build/data/
WEIGHTS=./build/float
DATASET=Tipu-12
GPU_ID=0
#QUANT_DIR=${QUANT_DIR:-quantized}
QUANT_DIR=./build/quantized
export PYTHONPATH=${PWD}:${PYTHONPATH}


echo "Conducting Quantization"
# fix calib
CUDA_VISIBLE_DEVICES=${GPU_ID} python code/test.py --resume ${WEIGHTS}/model_tipu12.pth --data_root ${DATA_DIR}/${DATASET} --quant_mode calib --quant_dir=${QUANT_DIR}

# fix test
CUDA_VISIBLE_DEVICES=${GPU_ID} python code/test.py --resume ${WEIGHTS}/model_tipu12.pth --data_root ${DATA_DIR}/${DATASET} --quant_mode test  --quant_dir=${QUANT_DIR}

# deploy
CUDA_VISIBLE_DEVICES=${GPU_ID} python code/test.py --resume ${WEIGHTS}/model_tipu12.pth --data_root ${DATA_DIR}/${DATASET} --quant_mode test  --quant_dir=${QUANT_DIR} --deploy --device=cpu



