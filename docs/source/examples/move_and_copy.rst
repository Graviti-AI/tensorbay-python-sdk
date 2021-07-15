###############
 Move And Copy
###############

This topic describes TensorBay dataset operations:

- :ref:`examples/move_and_copy:Copy Segment`
- :ref:`examples/move_and_copy:Move Segment`
- :ref:`examples/move_and_copy:Copy Data`
- :ref:`examples/move_and_copy:Move Data`

Take the `Oxford-IIIT Pet <https://gas.graviti.cn/dataset/data-decorators/OxfordIIITPet>`_
as an example. Its structure looks like::

    datasets/
        test/
            Abyssinian_002.jpg
            ...
        trainval/
            Abyssinian_001.jpg
            ...

.. note::

   Before operating this dataset,
   `fork <https://gas.graviti.cn/dataset/data-decorators/OxfordIIITPet>`_ it first.

Get the dataset client.

.. literalinclude:: ../../../docs/code/move_and_copy.py
   :language: python
   :start-after: """Get Dataset Client"""
   :end-before: """"""

There are currently two segments: ``test`` and ``trainval``.

**************
 Copy Segment
**************

Copy segment ``test`` to ``test_1``.

.. literalinclude:: ../../../docs/code/move_and_copy.py
   :language: python
   :start-after: """Copy Segment"""
   :end-before: """"""

**************
 Move Segment
**************

Move segment ``test`` to ``test_2``.

.. literalinclude:: ../../../docs/code/move_and_copy.py
   :language: python
   :start-after: """Move Segment"""
   :end-before: """"""

***********
 Copy Data
***********

Copy all data with prefix ``Abyssinian`` in both ``test_1`` and ``trainval``
segments to ``abyssinian`` segment.

.. literalinclude:: ../../../docs/code/move_and_copy.py
   :language: python
   :start-after: """Copy Data"""
   :end-before: """"""

***********
 Move Data
***********

Split ``trainval`` segment into ``train`` and ``val``:

#. Extract 500 data from ``trainval`` to ``val`` segment.
#. move ``trainval`` to ``train``.

.. literalinclude:: ../../../docs/code/move_and_copy.py
   :language: python
   :start-after: """Move Data"""
   :end-before: """"""

.. note::

   The data storage space will only be calculated once when a segment is copied.

.. note::

  TensorBay SDK supports three strategies to solve the conflict when the target segment/data already exists,
  which can be set as an keyword argument in the above-mentioned functions.

    - abort(default): abort the process by raising ResponseSystemError.
    - skip: skip moving or copying segment/data.
    - override: override the whole target segment/data with the source segment/data.
