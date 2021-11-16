#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
"""The template for example rst files."""

EXAMPLES_TEMPLATE = '''
######################################
 {dataset_name}
######################################

This topic describes how to manage the `{dataset_name} Dataset <https://gas.graviti.cn/dataset/
data-decorators/{file_name}>`_, which is a dataset with
:ref:`reference/label_format/{label_type}:{label_type}` label
{figure_description}

*****************************
 Authorize a Client Instance
*****************************

An :ref:`reference/glossary:accesskey` is needed to authenticate identity when using TensorBay.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Authorize a Client Instance"""
   :end-before: """"""

****************
 Create Dataset
****************

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Create Dataset"""
   :end-before: """"""

******************
 Organize Dataset
******************

Normally, ``dataloader.py`` and ``catalog.json`` are required to organize the "{dataset_name}"
dataset into the :class:`~tensorbay.dataset.dataset.Dataset` instance.
In this example, they are stored in the same directory like::

    {dataset_name}/
        catalog.json
        dataloader.py

Step 1: Write the Catalog
=========================

A :ref:`reference/dataset_structure:catalog` contains all label information of one dataset, which
is typically stored in a json file like ``catalog.json``.
{catalog_description}

{category_attribute_description}

.. note::

   By passing the path of the ``catalog.json``, :func:`~tensorbay.dataset.dataset.DatasetBase.
   load_catalog` supports loading the catalog into dataset.

.. important::

   See :ref:`catalog table <reference/dataset_structure:catalog>` for more catalogs with different
   label types.

Step 2: Write the Dataloader
============================

A :ref:`reference/glossary:dataloader` is needed to organize the dataset into a :class:`~tensorbay.
dataset.dataset.Dataset` instance.

.. literalinclude:: ../../../../../tensorbay/opendataset/{file_name}/loader.py
   :language: python
   :name: {file_name}-dataloader
   :linenos:

See :ref:`{label_type} annotation <reference/label_format/{label_type}:{label_type}>` for more
details.

There are already a number of dataloaders in TensorBay SDK provided by the community.
Thus, instead of writing, importing an available dataloader is also feasible.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Organize dataset / import dataloader"""
   :end-before: """"""

.. note::

   Note that catalogs are automatically loaded in available dataloaders, users do not have to write
   them again.

.. important::

   See :ref:`dataloader table <reference/glossary:dataloader>` for dataloaders with different label
   types.

*******************
 Visualize Dataset
*******************

Optionally, the organized dataset can be visualized by **Pharos**, which is a TensorBay SDK plug-in.
This step can help users to check whether the dataset is correctly organized.
Please see :ref:`features/visualization:Visualization` for more details.

****************
 Upload Dataset
****************

The organized "{dataset_name}" dataset can be uploaded to TensorBay for sharing, reuse, etc.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Upload Dataset"""
   :end-before: """"""

.. note::
   Set ``skip_uploaded_files=True`` to skip uploaded data.
   The data will be skiped if its name and segment name is the same as remote data.

Similar with Git, the commit step after uploading can record changes to the dataset as a version.
If needed, do the modifications and commit again.
Please see :ref:`features/version_control/index:Version Control` for more details.

**************
 Read Dataset
**************

Now "{dataset_name}" dataset can be read from TensorBay.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Read Dataset / get dataset"""
   :end-before: """"""

Get the segment names by listing them all.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Read Dataset / list segment names"""
   :end-before: """"""

Get a segment by passing the required segment name.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Read Dataset / get segment"""
   :end-before: """"""

In the :ref:`reference/dataset_structure:segment`, there is a sequence of
:ref:`reference/dataset_structure:data`, which can be obtained by index.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Read Dataset / get data"""
   :end-before: """"""

In each :ref:`reference/dataset_structure:data`,
there is a sequence of :ref:`reference/label_format/{label_type}:{label_type}` annotations,
which can be obtained by index.

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Read Dataset / get label"""
   :end-before: """"""

There is only one label type in "{dataset_name}" dataset, which is ``{label_type}``.
{information_description}

****************
 Delete Dataset
****************

.. literalinclude:: ../../../../../docs/code/{file_name}.py
   :language: python
   :start-after: """Delete Dataset"""
   :end-before: """"""
'''
