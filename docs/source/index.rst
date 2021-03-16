####################
 What is TensorBay?
####################

As an expert in unstructured data management, `TensorBay`_ provides services like data hosting,
complex data version management, online data visualization, and data collaboration.
TensorBay's unified authority management makes your data sharing and collaborative use more secure.

This documentation describes
:ref:`SDK <quick_start/getting_start_with_tensorbay:Getting Start with TensorBay>` and
:ref:`CLI <tensorbay_cli/getting_start_with_CLI:Getting Start with CLI>` tools for using TensorBay.

.. _TensorBay: https://www.graviti.cn/


############################
 What can TensorBay SDK do? 
############################

TensorBay Python SDK is a python library to access TensorBay and manage your datasets.
It provides:

- A :ref:`pythonic way <quick_start/getting_start_with_tensorbay:Getting Start with TensorBay>`
  to access your TensorBay resources by TensorBay `OpenAPI`_.
- An easy-to-use CLI tool :ref:`gas <tensorbay_cli/getting_start_with_CLI:Getting Start with CLI>`
  (Graviti AI service) to communicate with TensorBay.
- A consistent :ref:`dataset structure <reference/dataset_structure:Dataset Structure>`
  to read and write your datasets.

.. _OpenAPI: https://docs.graviti.cn/dev-doc/tools/api-center


.. toctree::
   :maxdepth: 1
   :caption: Quick Start

   quick_start/getting_start_with_tensorbay
   quick_start/examples

.. toctree::
   :maxdepth: 1
   :caption: Features

   features/dataset_management
   features/version_control

.. toctree::
   :maxdepth: 1
   :caption: Advanced Features

   advanced_features/fusion_dataset

.. toctree::
   :maxdepth: 1
   :caption: CLI

   tensorbay_cli/getting_start_with_CLI
   tensorbay_cli/dataset_management

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/glossary
   reference/dataset_structure
   reference/label_format
   reference/api_reference

..
   reference/release_note

..
.. toctree::
   :maxdepth: 1
   :caption: Community

   community/contribution
   community/roadmap
