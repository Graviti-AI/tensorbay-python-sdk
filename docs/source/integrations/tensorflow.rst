..
 Copyright 2021 Graviti. Licensed under MIT License.
 
############
 TensorFlow
############

This topic describes how to integrate TensorBay dataset with TensorFlow Pipeline
using the `MNIST Dataset <https://gas.graviti.com/dataset/hellodataset/MNIST>`_ as an example.

The typical method to integrate TensorBay dataset with TensorFlow is to build a callable "Segment" class.

.. literalinclude:: ../../../docs/code/use_dataset_in_tensorflow.py
   :language: python
   :start-after: """Build a Segment class"""
   :end-before:             # """"""

Using the following code to create a TensorFlow dataset and run it: 

.. literalinclude:: ../../../docs/code/use_dataset_in_tensorflow.py
   :language: python
   :start-after: """Build a tensorflow dataset and run it"""
   :end-before: """"""
