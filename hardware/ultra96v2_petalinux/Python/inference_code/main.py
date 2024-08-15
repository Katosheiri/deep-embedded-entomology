# -*- coding: utf-8 -*-

from ctypes import *
import numpy as np
import xir
import os
import math
import sys

from preprocess import *
from process import *
from inference import *


# Obtain DPU graph
def get_child_subgraph_dpu(graph):
    assert graph is not None, "'graph' should not be None."
    root_subgraph = graph.get_root_subgraph()
    assert (root_subgraph
            is not None), "Failed to get root subgraph of input Graph object."
    if root_subgraph.is_leaf:
        return []
    child_subgraphs = root_subgraph.toposort_child_subgraph()
    assert child_subgraphs is not None and len(child_subgraphs) > 0
    return [
        cs for cs in child_subgraphs
        if cs.has_attr("device") and cs.get_attr("device").upper() == "DPU"
    ]

def arg_to_name(class_file, inference_result, inference_result_name):
    # Read class names
    with open(class_file, 'r') as f:
        class_names = f.read().splitlines()

    # Read inference_result_arg
    with open(inference_result, 'r') as f:
        class_numbers = f.read().splitlines()

    # Transform arg into name
    class_labels = [class_names[int(num)] for num in class_numbers]

    # Write result in txt
    with open(inference_result_name, 'w') as f:
        for label in class_labels:
            f.write(label + '\n')
            
    print("arg to name done.")

def main(argv):
    # Init
    image_folder = "/path/to/image/folder"
    class_file = "/path/to/class/file"
    inference_result = "/path/to/output/arg"
    inference_result_name = "/path/to/output/name/"

    # get subgraphs
    g = xir.Graph.deserialize(argv[1])
    subgraphs = get_child_subgraph_dpu(g)

    num_thread = 4

    show_all_info = False
    evaluate_on_thread_range = False

    if evaluate_on_thread_range==True:
        for i in range(num_thread):
            predictions_list = test_accuracy(subgraphs, image_folder, class_file, i+1, show_all_info, inference_result)
            
    else:
        predictions_list = test_accuracy(subgraphs, image_folder, class_file, num_thread, show_all_info, inference_result)

    # Convert args into names
    arg_to_name(class_file, inference_result, inference_result_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage : python3 resnet50.py <resnet50_xmodel_file>")
    else:
        main(sys.argv)
