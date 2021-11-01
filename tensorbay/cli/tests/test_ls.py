#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.cli.cli import ls
from tensorbay.cli.tests.conftest import assert_cli_fail, assert_cli_success


@pytest.mark.parametrize("is_fusion", [True, False])
def test_ls(
    mocker,
    invoke,
    is_fusion,
    mock_get_dataset,
    mock_list_datasets,
    mock_list_segments,
    mock_paths,
    mock_get_data,
):
    params = {
        "offset": 0,
        "limit": 128,
    }

    list_datasets, datasets_response = mock_list_datasets(mocker)
    dataset_names = [dataset["name"] for dataset in datasets_response["datasets"]]
    dataset_name = dataset_names[0]
    dataset_output = "\n".join(f"tb:{name}" for name in dataset_names)
    result = invoke(ls, ["-l"])
    assert_cli_success(result, f"total {len(dataset_names)}\n{dataset_output}\n")
    list_datasets.assert_called_with("GET", "", params=params)

    get_datasets, _ = mock_get_dataset(mocker, is_fusion, False)
    get_segments, segments_response = mock_list_segments(mocker)

    segment_names = [segment["name"] for segment in segments_response["segments"]]
    segment_name = segment_names[0]
    segment_output = "\n".join(f"tb:{dataset_name}:{name}" for name in segment_names)
    result = invoke(ls, [f"tb:{dataset_name}"])
    assert_cli_success(result, f"{segment_output}\n")

    result = invoke(ls, [f"tb:{dataset_name}", "-l"])
    assert_cli_success(result, f"total {len(segment_names)}\n{segment_output}\n")

    list_paths, paths = mock_paths(mocker)
    remote_path = paths[0]

    result = invoke(ls, [f"tb:{dataset_name}:{segment_name}", "-l"])
    if is_fusion:
        assert_cli_fail(result, "ERROR: List fusion segment is not supported yet\n")
    else:
        path_output = "\n".join(f"tb:{dataset_name}:{segment_name}://{path}" for path in paths)
        assert_cli_success(result, f"total {len(paths)}\n{path_output}\n")

    result = invoke(ls, [f"tb:{dataset_name}", "-l", "-a"])
    if is_fusion:
        assert_cli_fail(result, 'ERROR: "-a" flag is not supported for fusion dataset yet\n')
    else:
        path_output = "\n".join(
            f"tb:{dataset_name}:{segment_name}://{path}"
            for segment_name in segment_names
            for path in paths
        )
        assert_cli_success(result, f"total {len(segment_names)*len(paths)}\n{path_output}\n")
        list_paths.assert_called_with()

    mock_get_data(mocker, remote_path)
    tbrn = f"tb:{dataset_name}:{segment_name}://{remote_path}"
    result = invoke(ls, [tbrn])
    if is_fusion:
        assert_cli_fail(result, "ERROR: List data in fusion segment is not supported yet\n")
    else:
        assert_cli_success(result, f"{tbrn}\n")

    segments_params = {"commit": "4", "offset": 0, "limit": 128}
    get_datasets.assert_called_with(dataset_name)
    get_segments.assert_called_with("GET", "segments", "123456", params=segments_params)
