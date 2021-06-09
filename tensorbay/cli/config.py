#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

import sys

import click

from .utility import is_accesskey, read_config, update_config, write_config


def _implement_config(key: str, value: str) -> None:
    update_config()
    config_parser = read_config()

    if is_accesskey(key):
        click.secho(
            "DeprecationWarning: Setting AccessKey in 'gas config'"
            " is deprecated since version v1.7.0. "
            "It will be removed in version v1.9.0. "
            "Use 'gas auth Accesskey' instead.",
            fg="red",
            err=True,
        )
        sys.exit(1)

    if key == "editor" and value:
        if not config_parser.has_section("config"):
            config_parser.add_section("config")
        config_parser["config"][key] = value
        write_config(config_parser)
