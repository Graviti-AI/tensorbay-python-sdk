################################
 Getting started with TensorBay
################################

**************
 Installation
**************

To install TensorBay SDK and CLI by **pip**, run the following command:

.. code:: console

   $ pip3 install tensorbay

To verify the SDK and CLI version, run the following command:

.. code:: console

   $ gas --version
   0.0.1


**************
 Registration
**************

Before using TensorBay SDK, please finish the following registration steps:

- Please visit `Graviti AI Service(GAS)`_ to sign up.
- Please visit `this page <https://gas.graviti.cn/access-key>`_ to get an AccessKey.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay

.. note::
   An AccessKey is needed to authenticate identity when using TensorBay via SDK or CLI.


*******
 Usage
*******

Authorize a Client Object
=========================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 11-13

See :ref:`this page <tensorbay_cli/getting_start_with_CLI:Config>` for details
about authenticating identity via CLI.

Create a Dataset 
================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 16

List Dataset Names
==================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 19

Upload Images to the Dataset
============================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 22-33

Read Images from the Dataset
============================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 36-47

Delete the Dataset
==================

.. literalinclude:: ../../../examples/getting_start_with_tensorbay.py
      :language: python
      :lines: 50
