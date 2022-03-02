..
 Copyright 2021 Graviti. Licensed under MIT License.
 
###############
 Visualization
###############

**Pharos** is a plug-in of TensorBay SDK used for local visualization.
After finishing the :ref:`dataset organization <features/dataset_management:Organize Dataset>`,
users can visualize the organized :class:`~tensorbay.dataset.dataset.Dataset` instance locally using **Pharos**.
The visualization result can help users to check whether the dataset is correctly organized.

***************
Install Pharos
***************

To install **Pharos** by **pip**, run the following command:

.. code:: console

   $ pip3 install pharos


**************
 Pharos Usage
**************


Organize a Dataset
==================

Take the :ref:`BSTLD <quick_start/examples/BSTLD:Organize Dataset>` as an example:

.. literalinclude:: ../../../docs/code/pharos.py
      :language: python
      :start-after: """Organize a Dataset"""
      :end-before: """"""

Visualize the Dataset
=====================

.. literalinclude:: ../../../docs/code/pharos.py
      :language: python
      :start-after: """Visualize The Dataset"""
      :end-before: """"""

Open the returned URL to see the visualization result.

.. _visualization result:

.. figure:: /images/visualization.jpg
   :align: center

   The visualized result of the BSTLD dataset.

.. note::

    By default, a pharos server runs locally at ``127.0.0.1:5000`` and is accessible only from localhost.
    To change the default setting, the following arguments in ``visualize()`` can be set:

    *  ``port``: the port the server runs in
    *  ``host``: the host ip to listen on

Visualize the Dataset on Remote Server
======================================

Pharos supports accessing the server remotely via a web browser by setting ``host`` to ``"0.0.0.0"``.
Then open ``http://{external IP}:{port}`` in the local browser to get the page.
The ``external IP`` is external ip of the server which pharos runs on.

.. literalinclude:: ../../../docs/code/pharos.py
      :language: python
      :start-after: """Visualize The Dataset On Remote Server"""
      :end-before: """"""
