#############
 Quick Start
#############

**************
 Installation
**************

To install TensorBay SDK and CLI by **pip**, run the following command:

.. code:: console

   pip3 install tensorbay


**************
 Verification
**************

To verify the SDK and CLI version, run the following command:

.. code:: console

   gas --version


**************
 Registration 
**************

Users can use local features without registration to do operations
such as :ref:`quick_start:Create Dataset from Local`.
But if users want to use cloud features to do operations
such as :ref:`quick_start:Read Dataset from TensorBay`, registration is required.

Please visit `Graviti AI Service(GAS)`_ to sign up.

.. _graviti ai service(gas): https://www.graviti.cn/tensorBay


****************
 Authentication
****************

An AccessKey is needed to authenticate identity on TensorBay via SDK or CLI.
See `this page <https://gas.graviti.cn/access-key>`_ for how to get an AccessKey.

To authenticate identity via SDK, initialize a ``GAS`` client by AccessKey:

.. code:: python

   from tensorbay import GAS

   ACCESS_KEY = "Accesskey-*****"
   # Create a gas client.
   gas = GAS(ACCESS_KEY)

See :ref:`this page <features/tensorbay_cli:TensorBay CLI>` for details
about authenticating identity via CLI.

***************************
 Create Dataset from Local
***************************

Consider that there is a directory `images`, and it contains 10 images.

.. code::

   images/
     0000.jpg
     0001.jpg
     0002.jpg
     0003.jpg
     0004.jpg
     0005.jpg
     0006.jpg
     0007.jpg
     0008.jpg
     0009.jpg

Run the following code to create a dataset containing these images:

.. code:: python

   import os
   from tensorbay.dataset import Data, Dataset

   # Create a dataset.
   dataset = Dataset("a_dataset_demo")
   # Create a segment with name "".
   segment = dataset.create_segment()
   # Create data.
   for image_name in os.listdir("images"):
       data = Data(os.path.join("images", image_name))
       segment.append(data)


***********************************
 Upload Local Dataset to TensorBay
***********************************

Run the following code to upload the dataset created above:

.. code:: python

   gas.create_dataset(dataset.name)
   dataset_client = gas.upload_dataset_object(dataset)
   dataset_client.commit()


*****************************
 Read Dataset from TensorBay
*****************************

Run the following code to read the uploaded dataset above.

.. code:: python

   from PIL import Image

   dataset_client = gas.get_dataset("a_dataset_demo")
   segment = dataset_client.get_segment_object()
   data = segment[0]
   image = Image.open(data.open())
