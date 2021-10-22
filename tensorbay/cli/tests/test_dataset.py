#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

import pytest

from tensorbay.cli.cli import dataset


@pytest.mark.parametrize("is_fusion", [True, False])
def test_dataset(
    mocker,
    invoke,
    is_fusion,
    mock_list_datasets,
    mock_create_dataset,
    mock_delete_dataset,
    mock_get_dataset,
):
    list_params = {
        "offset": 0,
        "limit": 128,
    }
    dataset_name = "test_dataset"
    tbrn = f"tb:{dataset_name}"
    wrong_tbrn = f"tb:{dataset_name}:test"
    create_params = {
        "name": dataset_name,
        "type": 0,
        "alias": "",
        "isPublic": False,
    }
    delete_hint = f'Dataset "{tbrn}" will be completely deleted.\nDo you want to continue? [y/N]:'
    succeed_hint = f'Successfully deleted dataset "{tbrn}"\n'

    list_datasets, datasets_response = mock_list_datasets(mocker)
    dataset_output = "".join(
        f'tb:{new_dataset["name"]}\n' for new_dataset in datasets_response["datasets"]
    )
    result = invoke(dataset)
    assert result.exit_code == 0
    assert result.output == dataset_output
    list_datasets.assert_called_with("GET", "", params=list_params)

    result = invoke(dataset, ["-d"])
    assert result.exit_code == 1
    assert result.stderr == "ERROR: Missing argument TBRN\n"

    result = invoke(dataset, [wrong_tbrn])
    assert result.exit_code == 1
    assert result.stderr == f'ERROR: "{wrong_tbrn}" is not a dataset\n'

    create_dataset, _ = mock_create_dataset(mocker)
    result = invoke(dataset, [tbrn])
    assert result.exit_code == 0
    assert result.output == f'Successfully created dataset "tb:{dataset_name}"\n'
    create_dataset.assert_called_with("POST", "", json=create_params)

    delete_dataset, delete_response = mock_delete_dataset(mocker, False, False, mock_get_dataset)
    result = invoke(dataset, [tbrn, "-d"], "y")
    assert result.exit_code == 0
    assert result.output == f"{delete_hint} y\n{succeed_hint}"

    result = invoke(dataset, [tbrn, "-d"], "N")
    assert result.exit_code == 1
    assert result.output == f"{delete_hint} N\n"

    result = invoke(dataset, [tbrn, "-d", "-y"])
    assert result.exit_code == 0
    assert result.output == succeed_hint

    delete_dataset.assert_called_with("DELETE", "", delete_response["id"])
