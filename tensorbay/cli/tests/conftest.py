#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Pytest fixture config."""

import os
from functools import partial
from pathlib import Path
from typing import Callable

import pytest
from click.testing import CliRunner, Result
from pytest_mock import MockerFixture

from tensorbay.cli.utility import ContextInfo, form_profile_value


@pytest.fixture(name="context")  # type: ignore[misc]
def context_object(mocker: MockerFixture, tmp_path: Path) -> ContextInfo:
    """Get a ContextInfo instance containing the command context.

    Arguments:
        mocker: The mocker fixture.
        tmp_path: An instance of TempPathFactory.

    Returns:
        The ContextInfo instance.

    """
    path = tmp_path / "test_home"
    path.mkdir()
    mocker.patch(f"{os.__name__}.path.expanduser", return_value=path)

    access_key = "Accesskey-********************************"
    url = "https://gas.graviti.cn/"
    context = ContextInfo(access_key, url, "test")

    config_parser = context.config_parser
    config_parser.add_section("profiles")
    profiles = config_parser["profiles"]
    profiles["test"] = form_profile_value(access_key, "")
    profiles["test_01"] = form_profile_value(access_key, "")
    profiles["test_02"] = form_profile_value(access_key, url)
    context.write_config(False)

    return context


@pytest.fixture()  # type: ignore[misc]
def invoke(context: ContextInfo) -> Callable[..., Result]:
    """Get a partial object of CliRunner.invoke.

    Arguments:
        context: The ContextInfo instance.

    Returns:
        The partial object.

    """
    runner = CliRunner(mix_stderr=False)
    return partial(runner.invoke, obj=context, catch_exceptions=False)


def assert_cli_success(result: Result, stdout: str) -> None:
    """Test if cli command is successful, output message is equal.

    Arguments:
        result: The Result instance.
        stdout: Output message.

    """
    assert result.exit_code == 0
    assert result.stdout == stdout


def assert_cli_fail(result: Result, stderr: str) -> None:
    """Test if cli command is failed, output message is equal.

    Arguments:
        result: The Result instance.
        stderr: Output message.

    """
    assert result.exit_code == 1
    assert result.stderr == stderr
