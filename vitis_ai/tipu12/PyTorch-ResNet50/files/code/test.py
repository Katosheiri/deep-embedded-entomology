#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright © 2023 Advanced Micro Devices, Inc. All rights reserved.
SPDX-License-Identifier: MIT
'''

import os
import argparse
import torch
import torch.nn.functional as F
import torch.optim as optim
import torchvision.models as models
from torchvision import datasets, transforms
from torchvision.datasets.folder import make_dataset, IMG_EXTENSIONS

import numpy as np
import cv2
from PIL import Image
import scipy.io as scio
from resnet import resnet18, resnet34, resnet50

import timm
import torch.nn as nn

## ImageNet size
IMG_W = np.short(224)
IMG_H = np.short(224)

def test(model, device, test_loader, deploy=False):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.cross_entropy(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()
            if deploy:
                return

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.3f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
        
        
def update_state_dict_keys(state_dict, prefix=''):
    updated_state_dict = {}
    for key, value in state_dict.items():
        new_key = key
        if prefix and key.startswith(prefix):
            new_key = key[len(prefix):]
        updated_state_dict[new_key] = value
    return updated_state_dict

def load_model_with_prefix(model, state_dict_path, prefix='0.'):
    state_dict = torch.load(state_dict_path, map_location=torch.device('cpu'))
    state_dict = update_state_dict_keys(state_dict, prefix)
    model.load_state_dict(state_dict)
    

def main():

    print("\nimage size is ", IMG_W, "cols x ", IMG_H, " rows\n" )
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch ResNet50')
    parser.add_argument('--batch-size', type=int, default=32, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--backbone', type=str, default='resnet50', help='backbone from resnet18,resnet34,resnet50')
    parser.add_argument('--test-batch-size', type=int, default=32, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--resume', type=str, default='', help='For resume model')
    parser.add_argument('--data_root', type=str, default='./build/data', help='dataset')
    # ------quantize---------
    parser.add_argument("--quant_dir", default='./build/quantized')
    parser.add_argument("--quant_mode", default="float", type=str)
    parser.add_argument("--device", default="cpu", type=str) 
    parser.add_argument("--deploy", action='store_true')
    parser.add_argument('--class_mapping', type=str, default='./build/data/Tipu-12/class_to_order.txt', help='Path to class mapping file')
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device('cpu')
    print(f"Testing on {device} device.")

    data_root = args.data_root 

    if args.deploy:
        args.test_batch_size = 1
        BATCH_SIZE = 1
    else:
        BATCH_SIZE = 32
    

    val_transform = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
             
    test_set = datasets.ImageFolder(
                os.path.join(data_root.rstrip('/'), 'test'),
                transform=val_transform)
    
    test_loader = torch.utils.data.DataLoader(test_set, batch_size=BATCH_SIZE, shuffle=False, drop_last=False, num_workers=4)
    
    num_classes = len(test_set.classes)
    print('test num:', len(test_set))
    print('classes:', test_set.classes)

    if args.backbone == 'resnet18':
        model = resnet18(num_classes=num_classes).to(device)
    elif args.backbone == 'resnet34':
        model = resnet34(num_classes=num_classes).to(device)
    elif args.backbone == 'resnet50':
        model = timm.create_model("resnet50.a1_in1k", pretrained=True, num_classes=12).to(device)
    else:
        print('error')
        return

    if args.resume != '':
        #model.load_state_dict(torch.load(args.resume, map_location=torch.device('cpu')))
        load_model_with_prefix(model, args.resume)	

    print("Model loaded and ready for testing")

    if not args.quant_mode == 'float':
        from pytorch_nndct.apis import torch_quantizer
        input = torch.randn([1, 3, IMG_H, IMG_W], dtype=torch.float32).to(device)
        quantizer = torch_quantizer(args.quant_mode, model, (input), output_dir = args.quant_dir, device=device)
        model = quantizer.quant_model
        print("Quantization applied")

    test(model, device, test_loader, args.deploy)

    if args.quant_mode == 'calib':
        quantizer.export_quant_config()
        print("Quantization config exported")

    if args.deploy:
        quantizer.export_xmodel(args.quant_dir, deploy_check=True)
        quantizer.export_torch_script(output_dir=args.quant_dir)
        quantizer.export_onnx_model(output_dir=args.quant_dir)
        print("Models exported for deployment")


if __name__ == '__main__':
    main()

