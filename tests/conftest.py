#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# type: ignore

"""Pytest fixture config."""

import pytest


def pytest_addoption(parser):
    """Register two command line option.

    Arguments:
        parser: Parser for command line arguments and ini-file values.

    """
    parser.addoption("--accesskey")
    parser.addoption("--url")


@pytest.fixture
def accesskey(request):
    """Get the accesskey from command line.

    Arguments:
        request: Gives access to the requesting test context.

    Returns:
        A accesskey from command line.

    """
    return request.config.getoption("--accesskey")


@pytest.fixture
def url(request):
    """Get and return the url from command line.

    Arguments:
        request: Gives access to the requesting test context.

    Returns:
        A url from command line.

    """
    return request.config.getoption("--url")
