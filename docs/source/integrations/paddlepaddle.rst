###############
 PaddlePaddle
###############

This topic describes how to integrate TensorBay dataset with PaddlePaddle Pipeline
using the `MNIST Dataset <https://gas.graviti.cn/dataset/data-decorators/MNIST>`_ as an example.

The typical method to integrate TensorBay dataset with PaddlePaddle is to build a "Segment" class
derived from ``paddle.io.Dataset``.

.. literalinclude:: ../../../docs/code/use_dataset_in_paddlepaddle.py
   :language: python
   :start-after: """Build a Segment class"""
   :end-before: """"""

Using the following code to create a PaddlePaddle dataloader and run it:

.. literalinclude:: ../../../docs/code/use_dataset_in_paddlepaddle.py
   :language: python
   :start-after: """Build a dataloader and run it"""
   :end-before: """"""