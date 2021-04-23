#################
 Update Dataset
#################

This topic describes how to update datasets, including:

- :ref:`examples/update_dataset:Update Label`
- :ref:`examples/update_dataset:Update Data`

.. note::
   Update data will instructions later.

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
   | uploading labels operation will overwrite all types of labels in data.

***************
 Update Data
***************

This part will be introduced later.
