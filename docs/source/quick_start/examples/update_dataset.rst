..
 Copyright 2021 Graviti. Licensed under MIT License.
 
#################
 Update Dataset
#################

This topic describes how to update datasets, including:

- :ref:`quick_start/examples/update_dataset:Update Dataset Meta`
- :ref:`quick_start/examples/update_dataset:Update Dataset Notes`
- :ref:`quick_start/examples/update_dataset:Update Label`
- :ref:`quick_start/examples/update_dataset:Update Data`

The following scenario is used for demonstrating how to update data and label:

#. Upload a dataset.
#. Update the dataset's labels.
#. Add some data to the dataset.

| Please see :ref:`features/dataset_management:Upload Dataset` for more information about the first step.
| The last two steps will be introduced in detail.

*********************
 Update Dataset Meta
*********************

TensorBay SDK supports a method to update dataset meta info.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update dataset meta"""
   :end-before: """"""

**********************
 Update Dataset Notes
**********************

TensorBay SDK supports a method to update :ref:`dataset notes <reference/dataset_structure:notes>`. The dataset can be updated into continuous
dataset by setting ``is_continuous`` to ``True``.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update dataset notes"""
   :end-before: """"""

***************
 Update Label
***************

TensorBay SDK supports methods to update labels to overwrite previous labels.

Get a previously uploaded dataset and create a draft:

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update label / get dataset an create draft"""
   :end-before: """"""

Update the catalog if needed:

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update label / update catalog"""
   :end-before: """"""

Overwrite previous labels with new label:

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update label / overwrite label"""
   :end-before: """"""

Commit the dataset:

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update label / commit dataset"""
   :end-before: """"""

| Now dataset is committed with a version including new labels.
| Users can switch between different commits to use different version of labels.

.. important::
   The operation to upload labels will overwrite all types of labels in data.

***************
 Update Data
***************

Add new data to dataset.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update data/ upload dataset"""
   :end-before: """"""

Set ``skip_uploaded_files=True`` to skip uploaded data.

Overwrite uploaded data to dataset.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update data/ overwrite dataset"""
   :end-before: """"""

The default value of ``skip_uploaded_files`` is ``False``, and use it to overwrite uploaded data.

.. note::
   The segment name and data name are used to identify data,
   if uploading a data whose segment name and data name are the same with certain data uploaded,
   then the former one will be visited.

.. important::
   The operation to upload data will only add or overwrite data, and the data uploaded before will not be deleted.

Delete segment by the segment name.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update data/ delete segment"""
   :end-before: """"""

Delete data by the data remote path.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Update data/ delete data"""
   :end-before: """"""

For a fusion dataset, TensorBay SDK supports deleting a frame by its id.

.. literalinclude:: ../../../../docs/code/update_dataset.py
   :language: python
   :start-after: """Delete frame"""
   :end-before: """"""
