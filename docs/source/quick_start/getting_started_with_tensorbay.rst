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

**************
 Registration
**************

Before using TensorBay SDK, please finish the following registration steps:

- Please visit `Graviti AI Service(GAS)`_ to sign up.
- Please visit `Graviti Developer Tools`_ to get an AccessKey.

.. _graviti ai service(gas): https://gas.graviti.cn/tensorbay/
.. _Graviti Developer Tools: https://gas.graviti.cn/tensorbay/developer

.. note::
   An AccessKey is needed to authenticate identity when using TensorBay via SDK or CLI.


*******
 Usage
*******

Authorize a Client Instance
============================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Authorize a Client Instance"""
      :end-before: """"""

See :ref:`CLI Configuration <tensorbay_cli/getting_started_with_cli:Configuration>` for
details about authenticating identity via CLI.


Create a Dataset 
================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Create a Dataset"""
      :end-before: """"""

List Dataset Names
==================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """List Dataset Names"""
      :end-before: """"""

Upload Images to the Dataset
============================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Upload Images to the Dataset"""
      :end-before: """"""

Read Images from the Dataset
============================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Read Images from the Dataset"""
      :end-before: """"""

Delete the Dataset
==================

.. literalinclude:: ../../../examples/getting_started_with_tensorbay.py
      :language: python
      :start-after: """Delete the Dataset"""
      :end-before: """"""
