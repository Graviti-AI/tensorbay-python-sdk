####################
 What is TensorBay?
####################

As an expert in unstructured data management, `TensorBay`_ provides services like data hosting,
complex data version management, online data visualization, and data collaboration.
TensorBay's unified authority management makes your data sharing and collaborative use more secure.

This documentation describes
:ref:`SDK <quick_start/getting_started_with_tensorbay:Getting Started with TensorBay>` and
:ref:`CLI <tensorbay_cli/getting_started_with_CLI:Getting Started with CLI>` tools for using TensorBay.

.. _TensorBay: https://www.graviti.cn/


############################
 What can TensorBay SDK do? 
############################

TensorBay Python SDK is a python library to access TensorBay and manage your datasets.
It provides:

- A :ref:`pythonic way <quick_start/getting_started_with_tensorbay:Getting Started with TensorBay>`
  to access TensorBay resources by TensorBay `OpenAPI`_.
- An easy-to-use CLI tool :ref:`gas <tensorbay_cli/getting_started_with_CLI:Getting Started with CLI>`
  (Graviti AI service) to communicate with TensorBay.
- A consistent :ref:`dataset structure <reference/dataset_structure:Dataset Structure>`
  to read and write datasets.

.. _OpenAPI: https://docs.graviti.cn/dev-doc/tools/api-center


.. toctree::
   :maxdepth: 1
   :caption: Quick Start

   quick_start/getting_started_with_tensorbay
   quick_start/examples/index

.. toctree::
   :maxdepth: 1
   :caption: Features

   features/dataset_management
   features/version_control/index
   features/visualization

.. toctree::
   :maxdepth: 1
   :caption: Advanced Features

   advanced_features/fusion_dataset/index
   advanced_features/storage_config
   advanced_features/request_configuration
   advanced_features/use_internal_endpoint
   advanced_features/profile
   advanced_features/cache

.. toctree::
   :maxdepth: 1
   :caption: Integrations

   integrations/paddlepaddle
   integrations/pytorch
   integrations/tensorflow

.. toctree::
   :maxdepth: 1
   :caption: CLI

   tensorbay_cli/getting_started_with_cli
   tensorbay_cli/tbrn
   tensorbay_cli/cli_commands
   tensorbay_cli/completion

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/glossary
   reference/dataset_structure
   reference/label_format/index
   reference/exception
   reference/api/index

..
   reference/release_note

.. toctree::
   :maxdepth: 1
   :caption: Community

..
   community/contribution
   community/roadmap
