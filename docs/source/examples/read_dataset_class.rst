######################
 Read "Dataset" Class
######################

This topic describes how to read the :class:~tensorbay.dataset.dataset.Dataset class
using the BSTLD_ dataset as an example.

.. _BSTLD: https://gas.graviti.cn/dataset/data-decorators/BSTLD

As mentioned in :ref:`features/dataset_management:Dataset Management`, a
:ref:`reference/glossary:Dataloader` is needed to get a :class:`~tensorbay.dataset.dataset.Dataset`.
However, there are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloader is also feasible.

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
   :start-after: """Organize dataset / import dataloader"""
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
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

This :ref:`reference/dataset_structure:Segment` is the same as the one :ref:`read from TensorBay <examples/BSTLD:Read Dataset>`.
In the train :ref:`reference/dataset_structure:Segment`, there is a sequence of :ref:`reference/dataset_structure:Data`,
which can be obtained by index.

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:Data`, there is a sequence of :ref:`reference/label_format:Box2D` annotations,
which can be obtained by index.

.. literalinclude:: ../../../examples/BSTLD.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""
