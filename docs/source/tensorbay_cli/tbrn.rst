#########################
 TensorBay Resource Name
#########################

TensorBay Resource Name(TBRN) uniquely defines the resource stored in TensorBay.
All TBRN begins with ``tb:``.

| 1. Define a dataset

.. code:: console

    tb:[dataset_name]

For example, the following TBRN means the dataset "VOC2012".

.. code:: console

    tb:VOC2012


| 2. Define a segment

.. code:: console

    tb:[dataset_name]:[segment_name]

For example, the following TBRN means the "train" segment of dataset "VOC2012".

.. code:: console

    tb:VOC2010:train


| 3. Define a file

.. code:: console

    tb:[dataset_name]:[segment_name]://[remote_path]

For example, the following TBRN means the file "2012_004330.jpg" under "train" segment in dataset "VOC2012".

.. code:: console

    tb:VOC2012:train://2012_004330.jpg


************************
 TBRN With Version Info
************************

The version information can also be included in the TBRN
when using :ref:`version control <features/version_control:Version Control>` feature.

| 1. Include revision info:

A TBRN can include revision info in the following format:

.. code:: console

   tb:[dataset_name]@[revision]:[segment_name]://[remote_path]

For example, the following TBRN means the main branch of dataset "VOC2012".

.. code:: console

    tb:VOC2010@main


| 2. Include draft info:

A TBRN can include draft info in the following format:

.. code:: console

   tb:[dataset_name]#[draft_number]:[segment_name]://[remote_path]

For example, the following TBRN means the 1st draft of dataset "VOC2012".

.. code:: console

    tb:VOC2012#1

Note that if neither revision nor draft number is given, a TBRN will refer to the default branch.
