#!/bin/sh

# Copyright © 2023 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

## Author: Daniele Bagni, AMD/Xilinx Inc
## date 26 May 2023


if [ $1 = kv260 ]; then
      ARCH=/workspace/tipu12/PyTorch-ResNet50/files/arch_kria_kv260.json
      TARGET=kv260
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR KV260.."
      echo "-----------------------------------------"
elif [ $1 = zcu104 ]; then
      ARCH=/opt/vitis_ai/compiler/arch/DPUCZDX8G/ZCU104/arch.json
      TARGET=zcu104
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR ZCU104.."
      echo "-----------------------------------------"
elif [ $1 = ultra96v2 ]; then
      ARCH=/workspace/tipu12/PyTorch-ResNet50/files/arch_ultra.json
      TARGET=ultra96v2
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR Ultra96v2.."
      echo "-----------------------------------------"
elif [ $1 = v70 ]; then
      ARCH=/opt/vitis_ai/compiler/arch/DPUCV2DX8G/V70/arch.json
      TARGET=v70
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR ALVEO V70.."
      echo "-----------------------------------------"
elif [ $1 = vek280 ]; then
    ARCH=/opt/vitis_ai/compiler/arch/DPUCV2DX8G/VEK280/arch.json
    TARGET=vek280
    echo "-----------------------------------------"
    echo "COMPILING MODEL FOR VEK280"
    echo "-----------------------------------------"
elif [ $1 = vck5000 ]; then
      ARCH=/opt/vitis_ai/compiler/arch/DPUCVDX8H/VCK50004PE/arch.json
      TARGET=vck5000
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR VCK5000"
      echo "-----------------------------------------"
elif [ $1 = kv260 ]; then
      ARCH=/Vitis_AI/Tutorials2/PyTorch-ResNet18/files/arch.json
      TARGET=kv260
      echo "-----------------------------------------"
      echo "COMPILING MODEL FOR KV260"
      echo "-----------------------------------------"


else
      echo  "Target not found. Valid choices are: zcu102, zcu104, vck190, vck5000, vek280, v70 ...exiting"
      exit 1
fi

CNN_MODEL=$2

compile() {
  vai_c_xir \
	--xmodel           build/quantized/${CNN_MODEL} \
	--arch            ${ARCH} \
	--output_dir      build/compiled_${TARGET} \
	--net_name        ${TARGET}_${CNN_MODEL}
#	--options         "{'mode':'debug'}"
#  --options         '{"input_shape": "1,224,224,3"}' \
}


compile #2>&1 | tee build/log/compile_$TARGET.log


echo "-----------------------------------------"
echo "MODEL COMPILED"
echo "-----------------------------------------"
