#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=invalid-name
# pylint: disable=pointless-string-statement
# type: ignore[arg-type]

"""This file includes the python code of interact with sextant application."""

"""Get sextant client"""
from tensorbay.apps.sextant import Sextant

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
sextant = Sextant("<YOUR_ACCESSKEY>")
""""""

"""List or get benchmarks"""
# list all benchmarks.
benchmarks = sextant.list_benchmarks()

# get benchmark with given name.
benchmark = sextant.get_benchmark("test_01")
""""""

"""Create evaluation"""
from tensorbay import GAS

# Please visit `https://gas.graviti.com/tensorbay/developer` to get the AccessKey.
gas = GAS("<YOUR_ACCESSKEY>")
dataset_client = gas.get_dataset("<DATASET_NAME>")
dataset_client.checkout(revision="<branch/tag/commitId>")
evaluation = benchmark.create_evaluation(dataset_client.dataset_id, dataset_client.status.commit_id)
""""""

"""List all evaluations"""
evaluations = benchmark.list_evaluations()
evaluation = evaluations[0]
""""""

"""Get evaluation result"""
result = evaluation.get_result()
""""""
