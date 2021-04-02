####################
 Dataset Management
####################

TensorBay CLI offers following sub-commands to manage your dataset.
(:numref:`Table. %s <sub_commands>`)

.. _sub_commands:

.. table:: Sub-Commands
   :align: center
   :widths: auto

   ============ =========================================
   Sub-Commands Description
   ============ =========================================
   create        Create a dataset
   ls            List data, segments and datasets
   delete        Delete a dataset
   ============ =========================================

****************
 Create dataset
****************

The basic structure of the sub-command to create a dataset with given name:

.. code:: console

   $ gas create [tbrn]

   tbrn:
       tb:[dataset_name]

Take `BSTLD`_ for example:

.. _BSTLD: https://gas.graviti.cn/dataset/data-decorators/BSTLD

.. code:: console

   $ gas create tb:BSTLD

**************
 Read Dataset
**************

The basic structure of the sub-command to List data, segments and datasets:

.. code:: console

   $ gas ls [Options] [tbrn]

   Options:
     -a, --all     List all files under all segments.
                    Only works when [tbrn] is tb:[dataset_name].

   tbrn:
     None
     tb:[dataset_name]
     tb:[dataset_name]:[segment_name]
     tb:[dataset_name]:[segment_name]://[remote_path]

If the path is empty, list the names of all datasets.
You can list data in the following ways:

| 1. List the names of all datasets.

.. code:: console

   $ gas ls

| 2. List the names of all segments of `BSTLD`_.

.. code:: console

   $ gas ls tb:BSTLD

| 3. List all the files in all the segments of `BSTLD`_.

.. code:: console

   $ gas ls -a tb:BSTLD

| 4. List all the files in the ``train`` segment of `BSTLD`_.

.. code:: console

   $ gas ls tb:BSTLD:train

****************
 Delete Dataset
****************

The basic structure of the sub-command to delete the dataset with given name:

.. code:: console

   $ gas delete [tbrn]

   tbrn:
     tb:[dataset_name]

Take `BSTLD`_ for example:

.. code:: console

   $ gas delete tb:BSTLD
