#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# type: ignore

"""This is the example code for using dataset in Pytorch."""


"""Build a Segment class"""
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from tensorbay import GAS
from tensorbay.dataset import Dataset as TensorBayDataset


class MNISTSegment(Dataset):
    """class for wrapping a MNIST segment."""

    def __init__(self, gas, segment_name, transform):
        super().__init__()
        self.dataset = TensorBayDataset("MNIST", gas)
        self.segment = self.dataset[segment_name]
        self.category_to_index = self.dataset.catalog.classification.get_category_to_index()
        self.transform = transform

    def __len__(self):
        return len(self.segment)

    def __getitem__(self, idx):
        data = self.segment[idx]
        with data.open() as fp:
            image_tensor = self.transform(Image.open(fp))

        return image_tensor, self.category_to_index[data.label.classification.category]
        # """"""


"""Build a dataloader and run it"""
ACCESS_KEY = "Accesskey-*****"

to_tensor = transforms.ToTensor()
normalization = transforms.Normalize(mean=[0.485], std=[0.229])
my_transforms = transforms.Compose([to_tensor, normalization])

train_segment = MNISTSegment(GAS(ACCESS_KEY), segment_name="train", transform=my_transforms)
train_dataloader = DataLoader(train_segment, batch_size=4, shuffle=True, num_workers=4)

for index, (image, label) in enumerate(train_dataloader):
    print(f"{index}: {label}")
""""""
