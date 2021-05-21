#########
 PyTorch
#########

This topic describes how to integrate TensorBay dataset with PyTorch Pipeline
using the `MNIST Dataset <https://gas.graviti.cn/dataset/data-decorators/MNIST>`_ as an example.

The typical method to integrate TensorBay dataset with PyTorch is to build a "Segment" class
derived from ``torch.utils.data.Dataset``.

.. literalinclude:: ../../../docs/code/use_dataset_in_pytorch.py
   :language: python
   :start-after: """Build a Segment class"""
   :end-before:         # """"""

Using the following code to create a PyTorch dataloader and run it: 

.. literalinclude:: ../../../docs/code/use_dataset_in_pytorch.py
   :language: python
   :start-after: """Build a dataloader and run it"""
   :end-before: """"""
