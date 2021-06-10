#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

import sys

import click

from .utility import error, is_accesskey, read_config, update_config, write_config


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

    if not config_parser.has_section("config"):
        config_parser.add_section("config")
    config_section = config_parser["config"]

    if not key:
        for config_key, config_value in config_section.items():
            click.echo(f"{config_key} = {config_value}\n")
        return

    if key != "editor":
        error(f"The option '{key}' is not supported to configure currently.\n")

    if not value:
        if key not in config_section:
            error(f"{key} has not been configured yet")
        click.echo(f"{key} = {config_section[key]}\n")
    else:
        config_section[key] = value
        write_config(config_parser)
