# TensorBay Python SDK

TensorBay Python SDK is a python library to access [TensorBay](https://www.graviti.cn/tensorBay)
and manage your datasets.  
It provides:

-   A pythonic way to access your TensorBay resources by TensorBay OpenAPI.
-   An easy-to-use CLI tool `gas` (Graviti AI service) to communicate with TensorBay.
-   A consistent dataset format to read and write your datasets.

## Installation

```console
pip3 install tensorbay
```

## Usage

An **AccessKey** is needed to communicate with TensorBay.
Please visit [this page](https://gas.graviti.cn/access-key) to get an **AccessKey** first.

### Authorize a client object

```python
from tensorbay import GAS
gas = GAS("<YOUR_ACCESSKEY>")
```

### Create a Dataset

```python
gas.create_dataset("DatasetName")
```

### List Dataset names

```python
# Method "list_dataset_names()" returns a iterator, use "list()" to transfer it to a "list".
dataset_list = list(gas.list_dataset_names())
```

### Upload images to the Dataset

```python
from tensorbay.dataset import Data, Dataset

# Organize the local dataset by the "Dataset" class before uploading.
dataset = Dataset("DatasetName")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment()

segment.append(Data("0000001.jpg"))
segment.append(Data("0000002.jpg"))

gas.upload_dataset_object(dataset)
```

### Read images from the Dataset

```python
from PIL import Image

dataset_client = gas.get_dataset("DatasetName")

segment = dataset_client.get_segment_object()

for data in segment:
    with data.open() as fp:
        image = Image(fp)
        width, height = image.size
        image.show()
```

### Delete the Dataset

```python
gas.delete_dataset("DatasetName")
```
