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

"""This file includes the python code of request_configuration.rst."""


"""Example of request config"""
from tensorbay import GAS
from tensorbay.client.requests import config
from tensorbay.opendataset import LISATrafficLight

config.timeout = 40
config.max_retries = 4

gas = GAS(access_key="Accesskey-***")

dataset = LISATrafficLight("/path/to/dataset")
gas.upload_dataset(dataset)
""""""
