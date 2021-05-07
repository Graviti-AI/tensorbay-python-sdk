#################
 Update Dataset
#################

This topic describes how to update datasets, including:

- :ref:`examples/update_dataset:Update Label`
- :ref:`examples/update_dataset:Update Data`

The following scenario is used for demonstrating how to update data and label:

#. Upload a dataset.
#. Update the dataset's labels.
#. Add some data to the dataset.

| Please see :ref:`features/dataset_management:Upload Dataset` for more information about the first step.
| The last two steps will be introduced in detail.

***************
 Update Label
***************

TensorBay SDK supports methods to update labels to overwrite previous labels.

Get a previously uploaded dataset and create a draft:

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Update label / get dataset an create draft"""
   :end-before: """"""

Update the catalog if needed:

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Update label / update catalog"""
   :end-before: """"""

Overwrite previous labels with new label on dataset:

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Update label / overwrite label"""
   :end-before: """"""

Commit the dataset:

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Update label / commit dataset"""
   :end-before: """"""

| Now dataset is committed with a version includes new labels.
| Users can switch between different commits to use different version of labels.

.. important::
   Uploading labels operation will overwrite all types of labels in data.

***************
 Update Data
***************

Add new data to dataset.

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Updata data/ upload dataset"""
   :end-before: """"""

Set `skip_uploaded_files=True` to skip uploaded data.

Overwrite uploaded data to dataset.

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Updata data/ overwrite dataset"""
   :end-before: """"""

The default value of `skip_uploaded_files` is false, use it to overwrite uploaded data.

.. note::
   The segment name and data name are used to identify data,
   which means if two data's segment names and data names are the same,
   then they will be regarded as one data.

.. important::
   Uploading dataset operation will only add or overwrite data, Data uploaded before will not be deleted.

Delete segment by the segment name.

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Updata data/ delete segment"""
   :end-before: """"""

Delete data by the file list.

.. literalinclude:: ../../../examples/update_dataset.py
   :language: python
   :start-after: """Updata data/ delete data"""
   :end-before: """"""
