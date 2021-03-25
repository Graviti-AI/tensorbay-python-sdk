######################
 Read "Dataset" Class
######################

This topic describes how to read the :class:`~tensorbay.dataset.dataset.Dataset` class after you have
:ref:`organized the "BSTLD" dataset <examples/BSTLD:Organize Dataset>`.
See `this page <https://www.graviti.cn/open-datasets/data-decorators/BSTLD>`_  for more details about this dataset.

As mentioned in :ref:`features/dataset_management:Dataset Management`, you need to write a
:ref:`reference/glossary:Dataloader` to get a :class:`~tensorbay.dataset.dataset.Dataset`.
However, there are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, you can just import an available dataloader.

The local directory structure for "BSTLD" should be like:

.. code:: console

   <path>
       rgb/
           additional/
               2015-10-05-10-52-01_bag/
                   <image_name>.jpg
                   ...
               ...
           test/
               <image_name>.jpg
               ...
           train/
               2015-05-29-15-29-39_arastradero_traffic_light_loop_bag/
                   <image_name>.jpg
                   ...
               ...
       test.yaml
       train.yaml
       additional_train.yaml

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """"Read Dataset Class / organize dataset"""
   :end-before: """"""

.. warning::

   Dataloaders provided by the community work well only with the original dataset directory structure.
   Downloading datasets from either official website or `Graviti Opendatset Platform`_ is highly
   recommended.

.. _graviti opendatset platform: https://www.graviti.cn/open-datasets

TensorBay supplies two methods to fetch :ref:`reference/dataset_structure:Segment` from
:ref:`reference/dataset_structure:Dataset`.

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """Read Dataset Class / get a segment"""
   :end-before: """"""

The :ref:`reference/dataset_structure:Segment` you get now is the same as the one you :ref:`read from TensorBay <examples/BSTLD:Read Dataset>`.
In the train :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`. You
can get one by index.

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`, there is a sequence of :ref:`reference/label_format:Box2D` annotations.
You can get one by index.

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""
