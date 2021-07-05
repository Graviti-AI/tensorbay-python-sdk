# TensorBay Python SDK

[![Pre-commit](https://github.com/Graviti-AI/tensorbay-python-sdk/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/Graviti-AI/tensorbay-python-sdk/actions/workflows/pre-commit.yaml)
[![Unit Test](https://github.com/Graviti-AI/tensorbay-python-sdk/actions/workflows/unit_test.yaml/badge.svg)](https://github.com/Graviti-AI/tensorbay-python-sdk/actions/workflows/unit_test.yaml)
[![Documentation Status](https://readthedocs.org/projects/tensorbay-python-sdk/badge/?version=latest)](https://tensorbay-python-sdk.graviti.com/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/tensorbay/month)](https://pepy.tech/project/tensorbay)
[![Coverage Status](https://coveralls.io/repos/github/Graviti-AI/tensorbay-python-sdk/badge.svg)](https://coveralls.io/github/Graviti-AI/tensorbay-python-sdk)
[![GitHub](https://img.shields.io/github/license/Graviti-AI/tensorbay-python-sdk)](https://github.com/Graviti-AI/tensorbay-python-sdk/blob/main/LICENSE)
[![Slack](https://img.shields.io/static/v1?label=slack&message=graviti&logo=slack&color=blueviolet)](https://join.slack.com/t/graviticommunity/shared_invite/zt-qivjowva-8RxtilBsHIf218sOsLTHOQ)
[![PyPI](https://img.shields.io/pypi/v/tensorbay)](https://pypi.org/project/tensorbay/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tensorbay)](https://pypi.org/project/tensorbay/)

---

**IMPORTANT**: TensorBay system underwent a huge refactoring, which broke the downward compatibility
of OpenAPI and SDK. As a result, the SDK under version v1.6.0 does not work anymore.  
**Please update tensorbay SDK to v1.6.0 or a higher version.**

---

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

## Documentation

More information can be found on the [documentation site](https://tensorbay-python-sdk.graviti.com/)

## Usage

An **AccessKey** is needed to communicate with TensorBay.
Please visit [this page](https://gas.graviti.cn/tensorbay/developer) to get an **AccessKey** first.

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
dataset_names = gas.list_dataset_names()
```

### Upload images to the Dataset

```python
from tensorbay.dataset import Data, Dataset

# Organize the local dataset by the "Dataset" class before uploading.
dataset = Dataset("DatasetName")

# TensorBay uses "segment" to separate different parts in a dataset.
segment = dataset.create_segment("SegmentName")

segment.append(Data("0000001.jpg"))
segment.append(Data("0000002.jpg"))

dataset_client = gas.upload_dataset(dataset, jobs=8)

# TensorBay provides dataset version control feature, commit the uploaded data before using it.
dataset_client.commit("Initial commit")
```

### Read images from the Dataset

```python
from PIL import Image

dataset = Dataset("DatasetName", gas)
segment = dataset[0]

for data in segment:
    with data.open() as fp:
        image = Image.open(fp)
        width, height = image.size
        image.show()
```

### Delete the Dataset

```python
gas.delete_dataset("DatasetName")
```
