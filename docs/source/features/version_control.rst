#################
 Version Control
#################

TensorBay currently supports the linear version control.
A new version of a dataset can be built upon the previous version.
:numref:`Figure. %s <version_control>` demonstrates the relations
between different versions of a dataset.

.. _version_control:

.. figure:: ../images/version_control.png
   :scale: 60 %
   :align: center

   The relations between different versions of a dataset.


********
 Commit
********

As mentioned in :ref:`quick start <quick_start:Upload Local Dataset to TensorBay>`,
after uploading a local dataset to TensorBay, a commit step should be done.
Actually, the commit step is used for turning a dataset from draft status into committed status.

There are scenarios when new versions of dataset are required,
such as correcting errors, enlarging dataset, adding more types of labels, etc.

Under these circumstances, you can continue editing the dataset based on the current version,
such as uploading some more data to it.
After finishing the editing, you can do the commit step again to create a new version.
Note that only committed versions can be used.
