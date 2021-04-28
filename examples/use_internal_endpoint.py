#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=not-callable
# pylint: disable=ungrouped-imports
# pylint: disable=import-error
# pylint: disable=pointless-string-statement
# pylint: disable=invalid-name

"""This file includes the python code of use_internal_network."""


"""Usage of Upload Dataset By Internal Endpoint"""
from tensorbay import GAS
from tensorbay.client.requests import config
from tensorbay.opendataset import LISATrafficLight

DATASET_NAME = "LISA Traffic Light"

config.is_internal = True

gas = GAS(access_key="Accesskey-***")
gas.create_dataset(DATASET_NAME)

dataset = LISATrafficLight("/path/to/dataset")
gas.upload_dataset(dataset)
""""""
