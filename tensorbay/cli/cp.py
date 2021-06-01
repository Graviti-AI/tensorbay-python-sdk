#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas cp."""

import os
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable

from ..dataset import Data, Segment
from .tbrn import TBRN, TBRNType
from .utility import error, get_dataset_client, get_gas


def _implement_cp(  # pylint: disable=too-many-arguments
    obj: Dict[str, str],
    local_paths: Iterable[str],
    tbrn: str,
    is_recursive: bool,
    jobs: int,
    skip_uploaded_files: bool,
) -> None:
    gas = get_gas(**obj)
    info = TBRN(tbrn=tbrn)

    dataset_client = get_dataset_client(gas, info, is_fusion=False)

    if info.type not in (TBRNType.SEGMENT, TBRNType.NORMAL_FILE):
        error(f'"{tbrn}" is not a segment or file type')

    target_remote_path = info.remote_path if info.type == TBRNType.NORMAL_FILE else ""

    local_abspaths = [os.path.abspath(local_path) for local_path in local_paths]
    if (
        len(local_abspaths) == 1
        and not os.path.isdir(local_abspaths[0])
        and target_remote_path
        and not target_remote_path.endswith("/")
    ):
        segment_client = dataset_client.get_or_create_segment(info.segment_name)
        segment_client.upload_file(local_abspaths[0], target_remote_path)
    else:
        segment = _get_segment(info.segment_name, local_abspaths, target_remote_path, is_recursive)
        dataset_client.upload_segment(segment, jobs=jobs, skip_uploaded_files=skip_uploaded_files)


def _get_segment(
    segment_name: str,
    local_abspaths: Iterable[str],
    remote_path: str,
    is_recursive: bool,
) -> Segment:
    """Get the pair of local_path and remote_path.

    Arguments:
        segment_name: The name of the segment these data belong to.
        local_abspaths: A list of local abstract paths, could be folder or file.
        remote_path: The remote object path, not necessarily end with '/'.
        is_recursive: Whether copy directories recursively.

    Returns:
        A segment contains mapping data.

    """
    segment = Segment(segment_name)
    for local_abspath in local_abspaths:
        if not os.path.isdir(local_abspath):
            data = Data(
                local_abspath,
                target_remote_path=str(PurePosixPath(remote_path, os.path.basename(local_abspath))),
            )
            segment.append(data)
            continue

        if not is_recursive:
            error("Local paths include directories, please use -r option")

        local_abspath = os.path.normpath(local_abspath)
        folder_name = os.path.basename(local_abspath)
        for root, _, filenames in os.walk(local_abspath):
            relpath = os.path.relpath(root, local_abspath) if root != local_abspath else ""
            for filename in filenames:
                data = Data(
                    os.path.join(root, filename),
                    target_remote_path=str(
                        PurePosixPath(Path(remote_path, folder_name, relpath, filename))
                    ),
                )
                segment.append(data)
    return segment
