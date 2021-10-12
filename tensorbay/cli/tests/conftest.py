#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Pytest fixture config."""

from collections import OrderedDict
from configparser import ConfigParser
from functools import partial
from typing import Callable

import pytest
from click.testing import CliRunner, Result

from tensorbay.cli.utility import ContextInfo


@pytest.fixture(scope="session", name="context")  # type: ignore[misc]
def context_object() -> ContextInfo:
    """Get a ContextInfo instance containing the command context.

    Returns:
        The ContextInfo instance.

    """
    obj: ContextInfo = object.__new__(ContextInfo)
    obj.access_key = "Accesskey-********************************"
    obj.url = "https://gas.graviti.cn/"
    obj.profile_name = "default"
    obj.config_parser = ConfigParser(dict_type=OrderedDict)

    return obj


@pytest.fixture(scope="session")  # type: ignore[misc]
def invoke(context: ContextInfo) -> Callable[..., Result]:
    """Get a partial object of CliRunner.invoke.

    Arguments:
        context: The ContextInfo instance.

    Returns:
        The partial object.

    """
    runner = CliRunner(mix_stderr=False)
    return partial(runner.invoke, obj=context, catch_exceptions=False)
