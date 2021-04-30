#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#

"""Graviti Tensorbay gas CLI utility functions."""

import logging
import os
import sys
from configparser import ConfigParser
from typing import Tuple

import click

from ..client import GAS
from ..client import config as client_config


def _implement_cli(
    ctx: click.Context, access_key: str, url: str, profile_name: str, debug: bool
) -> None:
    """You can use 'gas' + COMMAND to operate on your dataset.\f

    Arguments:
        ctx: The context to be passed as the first argument.
        access_key: The accessKey of gas.
        url: The login URL.
        profile_name: The environment to login.
        debug: Debug mode flag.

    """  # noqa: D301,D415
    ctx.obj = {
        "access_key": access_key,
        "url": url,
        "profile_name": profile_name,
    }
    client_config._x_source = "PYTHON-CLI"  # pylint: disable=protected-access

    if debug:
        logging.basicConfig(level=logging.DEBUG)


def get_config_filepath() -> str:
    """Get the path of the config file.

    Returns:
        The path of the config file.

    """
    home = "USERPROFILE" if os.name == "nt" else "HOME"
    return os.path.join(os.environ[home], ".gasconfig")


def read_config(config_filepath: str, profile_name: str) -> Tuple[str, str]:
    """Read accessKey and URL from the config file.

    Arguments:
        config_filepath: The file containing config info.
        profile_name: The environment to login.

    Returns:
        The accessKey of profile_name read from the config file.
        The URL of profile_name read from the config file.

    """
    if not os.path.exists(config_filepath):
        click.echo(
            f"{config_filepath} not exist"
            "\n\nPlease use 'gas config <accessKey>' to create config file",
            err=True,
        )
        sys.exit(1)

    config_parser = ConfigParser()
    config_parser.read(config_filepath)
    access_key = config_parser[profile_name]["accessKey"]
    url = config_parser[profile_name]["url"] if "url" in config_parser[profile_name] else ""
    return access_key, url


def get_gas(access_key: str, url: str, profile_name: str) -> GAS:
    """Load an object of :class:`~tensorbay.client.gas.GAS`.

    We will read accessKey and URL from the appointed profile_name and login gas.

    Arguments:
        access_key: The accessKey of gas.
        url: The login URL.
        profile_name: The environment to login.

    Returns:
        Gas client logged in with accessKey and URL.

    """
    if not access_key and not url:
        access_key, url = read_config(get_config_filepath(), profile_name)

    if not access_key:
        click.echo("accessKey should be appointed", err=True)
        sys.exit(1)

    return GAS(access_key, url)
