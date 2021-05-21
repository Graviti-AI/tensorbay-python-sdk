#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=too-few-public-methods
# type: ignore

"""This is the example code for using dataset in TensorFlow."""


"""Build a Segment class"""
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.data import Dataset

from tensorbay import GAS
from tensorbay.dataset import Dataset as TensorBayDataset


class MNISTSegment:
    """class for wrapping a MNIST segment."""

    def __init__(self, gas, segment_name):
        self.dataset = TensorBayDataset("MNIST", gas)
        self.segment = self.dataset[segment_name]
        self.category_to_index = self.dataset.catalog.classification.get_category_to_index()

    def __call__(self):
        """Yield an image and its corresponding label.

        Yields:
            image_tensor: the tensorflow sensor of the image.
            category_tensor: the tensorflow sensor of the category.

        """
        for data in self.segment:
            with data.open() as fp:
                image_tensor = tf.convert_to_tensor(
                    np.array(Image.open(fp)) / 255, dtype=tf.float32
                )
            category = self.category_to_index[data.label.classification.category]
            category_tensor = tf.convert_to_tensor(category, dtype=tf.int32)
            yield image_tensor, category_tensor
            # """"""


"""Build a tensorflow dataset and run it"""
ACCESS_KEY = "Accesskey-*****"

dataset = Dataset.from_generator(
    MNISTSegment(GAS(ACCESS_KEY), "train"),
    output_signature=(
        tf.TensorSpec(shape=(28, 28), dtype=tf.float32),
        tf.TensorSpec(shape=(), dtype=tf.int32),
    ),
).batch(4)

for index, (image, label) in enumerate(dataset):
    print(f"{index}: {label}")
""""""
