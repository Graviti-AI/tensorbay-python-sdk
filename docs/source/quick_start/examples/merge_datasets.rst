..
 Copyright 2021 Graviti. Licensed under MIT License.
 
################
 Merge Datasets
################

This topic describes the merge dataset operation.

Take the `Oxford-IIIT Pet <https://gas.graviti.com/dataset/graviti/OxfordIIITPet>`_
and `Dogs vs Cats <https://gas.graviti.com/dataset/graviti/DogsVsCats>`_
as examples. Their structures looks like::

    Oxford-IIIT Pet/
        test/
            Abyssinian_002.jpg
            ...
        trainval/
            Abyssinian_001.jpg
            ...

    Dogs vs Cats/
        test/
            1.jpg
            10.jpg
            ...
        train/
            cat.0.jpg
            cat.1.jpg
            ...

There are lots of pictures of cats and dogs in these two datasets, and now merge them to get a more diverse dataset.

.. note::

   Before merging datasets, fork both of the open datasets first.

Create a dataset which is named as ``mergedDataset``.

.. literalinclude:: ../../../../docs/code/merge_datasets.py
   :language: python
   :start-after: """Create Target Dataset"""
   :end-before: """"""

Copy all segments in ``OxfordIIITPetDog`` to ``mergedDataset``.

.. literalinclude:: ../../../../docs/code/merge_datasets.py
   :language: python
   :start-after: """Copy Segment From Pet"""
   :end-before: """"""

Use the catalog of OxfordIIITPet as the catalog of the merged dataset.

.. literalinclude:: ../../../../docs/code/merge_datasets.py
   :language: python
   :start-after: """Upload Catalog"""
   :end-before: """"""


Unify categories of ``train`` segment.

.. literalinclude:: ../../../../docs/code/merge_datasets.py
   :language: python
   :start-after: """Unify Category"""
   :end-before: """"""

.. note::

    The category in ``OxfordIIITPet`` is of two-level formats, like ``cat.Abyssinian``,
    but in ``Dogs vs Cats`` it only has one level, like ``cat``.
    Thus it is important to unify the categories, for example, rename ``cat.Abyssinian`` to ``cat``.

Copy data from ``Dogs vs Cats`` to ``mergedDataset``.

.. literalinclude:: ../../../../docs/code/merge_datasets.py
   :language: python
   :start-after: """Copy Data From Dog VS Cat"""
   :end-before: """"""
