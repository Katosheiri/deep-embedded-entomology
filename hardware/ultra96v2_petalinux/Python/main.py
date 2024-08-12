# -*- coding: utf-8 -*-

from ctypes import *
import numpy as np
import xir
import os
import math
import sys

from preprocess import *
from process import *
from test_accuracy import *


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

def main(argv):
    # Init
    image_folder = "resnet50_mt_py/test_tipu12"
    class_file = "resnet50_mt_py/words.txt"

    # get subgraphs
    g = xir.Graph.deserialize(argv[1])
    subgraphs = get_child_subgraph_dpu(g)

    # Load class names from the class_map file
    with open(class_file, "r") as file:
        class_names = [line.strip() for line in file.readlines()]

    num_classes = count_directories(image_folder)
    num_thread = 4

    show_all_info = False
    evaluate_on_thread_range = True

    if evaluate_on_thread_range==True:
        for i in range(num_thread):
            accuracy, class_accuracy, label_names, predictions_list, labels_list = test_accuracy(subgraphs, image_folder, class_file, num_classes, i+1, show_all_info)
            np.savetxt('class_accuracy.txt', class_accuracy, fmt='%f', delimiter=',')
            np.savetxt('predictions_list.txt', predictions_list, fmt='%s', delimiter=',')
            np.savetxt('labels_list.txt', labels_list, fmt='%s', delimiter=',')
            
    else:
        accuracy, class_accuracy, label_names, predictions_list, labels_list = test_accuracy(subgraphs, image_folder, class_file, num_classes, num_thread, show_all_info)
        np.savetxt('class_accuracy.txt', class_accuracy, fmt='%f', delimiter=',')
        np.savetxt('predictions_list.txt', predictions_list, fmt='%s', delimiter=',')
        np.savetxt('labels_list.txt', labels_list, fmt='%s', delimiter=',')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage : python3 resnet50.py <resnet50_xmodel_file>")
    else:
        main(sys.argv)
