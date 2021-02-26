#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Healthcheck related methods.

:meth:`healthcheck` finds all errors in the :class:`~tensorbay.dataset.dataset.Dataset`
or :class:`~tensorbay.dataset.dataset.FusionDataset`,
including basic errors and catalog errors.

"""

from typing import Union

from ..dataset import Dataset, FusionDataset
from .basic_check import check_basic
from .catalog_check import check_catalog
from .report import HealthReport


def healthcheck(dataset: Union[Dataset, FusionDataset]) -> HealthReport:
    """Healthcheck for Dataset or FusionDataset.

    Arguments:
        dataset: The :class:`~tensorbay.dataset.dataset.Dataset`
            or :class:`~tensorbay.dataset.dataset.FusionDataset` for healthchecking.

    Returns:
        The full result of the healthcheck which contains all errors found.

    """
    report = HealthReport()

    with report.basic_reports as basic_reports:
        for basic_error in check_basic(dataset):
            basic_reports.append(basic_error)

    with report.subcatalog_reports as subcatalog_reports:
        for label_type, attribute_info_error in check_catalog(dataset.catalog):
            subcatalog_reports[label_type].append(attribute_info_error)

    return report
