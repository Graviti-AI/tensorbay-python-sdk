#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas ls."""

from typing import Dict, Iterable, Optional

import click

from ..client import GAS
from ..client.dataset import FusionDatasetClient
from ..client.gas import DatasetClientType
from .tbrn import TBRN, TBRNType
from .utility import error, get_dataset_client, get_gas


def _echo_data(
    dataset_name: str,
    draft_number: Optional[int],
    revision: Optional[str],
    segment_name: str,
    data_iter: Iterable[str],
) -> None:
    """Echo files in data_iter under 'tb:dataset_name:segment_name'.

    Arguments:
        dataset_name: The name of the dataset the segment belongs to.
        draft_number: The draft number (if the status is draft).
        revision: The revision (if the status is not draft).
        segment_name: The name of the segment.
        data_iter: Iterable data to be echoed.

    """
    for data in data_iter:
        click.echo(
            TBRN(
                dataset_name,
                segment_name,
                remote_path=data,
                draft_number=draft_number,
                revision=revision,
            ).get_tbrn()
        )


def _validate_dataset_client(dataset_client: DatasetClientType) -> None:
    if not dataset_client.status.draft_number and not dataset_client.status.commit_id:
        error(f'"{dataset_client.name}" has no commit history.')


def _ls_dataset(gas: GAS, info: TBRN, list_all_files: bool, show_total_num: bool) -> None:
    dataset_client = get_dataset_client(gas, info)
    _validate_dataset_client(dataset_client)

    segment_names = dataset_client.list_segment_names()
    if not list_all_files:
        if show_total_num:
            click.echo(f"total {len(segment_names)}")
        for segment_name in segment_names:
            click.echo(TBRN(info.dataset_name, segment_name).get_tbrn())
        return

    if isinstance(dataset_client, FusionDatasetClient):
        error('"-a" flag is not supported for fusion dataset yet')

    segment_paths = [
        dataset_client.get_segment(segment_name).list_data_paths() for segment_name in segment_names
    ]
    if show_total_num:
        total = sum(len(segment_path) for segment_path in segment_paths)
        click.echo(f"total {total}")

    for segment_name, segment_path in zip(segment_names, segment_paths):
        _echo_data(
            info.dataset_name,
            info.draft_number,
            info.revision,
            segment_name,
            segment_path,
        )


def _ls_segment(
    gas: GAS,
    info: TBRN,
    list_all_files: bool,  # pylint: disable=unused-argument
    show_total_num: bool,
) -> None:
    dataset_client = get_dataset_client(gas, info)
    _validate_dataset_client(dataset_client)
    if isinstance(dataset_client, FusionDatasetClient):
        error("List fusion segment is not supported yet")

    segment_path = dataset_client.get_segment(info.segment_name).list_data_paths()
    if show_total_num:
        click.echo(f"total {len(segment_path)}")
    _echo_data(
        info.dataset_name,
        info.draft_number,
        info.revision,
        info.segment_name,
        segment_path,
    )


def _ls_normal_file(
    gas: GAS,  # pylint: disable=unused-argument
    info: TBRN,  # pylint: disable=unused-argument
    list_all_files: bool,  # pylint: disable=unused-argument
    show_total_num: bool,  # pylint: disable=unused-argument
) -> None:
    error("List for specific file is not supported yet")


_LS_FUNCS = {
    TBRNType.DATASET: _ls_dataset,
    TBRNType.SEGMENT: _ls_segment,
    TBRNType.NORMAL_FILE: _ls_normal_file,
}


def _implement_ls(
    obj: Dict[str, str], tbrn: str, list_all_files: bool, show_total_num: bool
) -> None:
    gas = get_gas(**obj)
    if not tbrn:
        dataset_names = gas.list_dataset_names()
        if show_total_num:
            click.echo(f"total {len(dataset_names)}")
        for dataset_name in dataset_names:
            click.echo(TBRN(dataset_name).get_tbrn())
        return

    info = TBRN(tbrn=tbrn)
    _LS_FUNCS[info.type](gas, info, list_all_files, show_total_num)
