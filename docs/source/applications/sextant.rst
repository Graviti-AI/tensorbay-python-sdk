..
 Copyright 2021 Graviti. Licensed under MIT License.
 
#########
 Sextant
#########

TensorBay SDK supports methods to interact with sextant application.
See `authorized storage instruction <https://docs.graviti.com/apps/sextant>`_ for details about how to start.

Authorize a Sextant Instance
============================

.. literalinclude:: ../../../docs/code/sextant.py
   :language: python
   :start-after: """Get sextant client"""
   :end-before: """"""

List or get benchmark
=====================

.. literalinclude:: ../../../docs/code/sextant.py
   :language: python
   :start-after: """List or get benchmarks"""
   :end-before: """"""

Create a evaluation
===================

A evaluation must be created by one commit.

.. literalinclude:: ../../../docs/code/sextant.py
   :language: python
   :start-after: """Create evaluation"""
   :end-before: """"""

List all evaluations
====================

.. literalinclude:: ../../../docs/code/sextant.py
   :language: python
   :start-after: """List all evaluations"""
   :end-before: """"""

get evaluation result
=====================

.. literalinclude:: ../../../docs/code/sextant.py
   :language: python
   :start-after: """Get evaluation result"""
   :end-before: """"""

The details of the result structure for the evaluation are as follows:

.. code-block::

   {
       "result": {
           "categories": {
               "aeroplane": {
                   "AP": 0.3,
                   "averageIoU": 0.71,
                   "pr": {
                       "precision": [0.87, 0.8, ...],
                       "recall": [0.001, 0.0045, ...]
                   }
               },
               ...
           },
           "overall": {
               "averageIoU": 0.7,
               "mAP": 0.2,
               "pr": {
                   "precision": [0.95, 0.91, ...],
                   "recall": [0.0036, 0.01, ...]
               }
           }
       }
   }

.. note::

    Benchmark can only be created with `tensorbay website <https://gas.graviti.com/apps/Sextant>`_ now.

