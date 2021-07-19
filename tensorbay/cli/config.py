#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

import click

from .utility import error, read_config, update_config, write_config


def _implement_config(key: str, value: str, unset: bool) -> None:
    _check_args_and_options(key, value, unset)

    update_config()
    config_parser = read_config()

    if not config_parser.has_section("config"):
        config_parser.add_section("config")
    config_section = config_parser["config"]

    if not key:
        for config_key, config_value in config_section.items():
            click.echo(f"{config_key} = {config_value}\n")
        return

    if not value:
        if key not in config_section:
            error(f"{key} has not been configured yet")
        if unset:
            del config_section[key]
            write_config(config_parser, show_message=False)
            click.echo(f'Unset "{key}" successfully')
            return

        click.echo(f"{key} = {config_section[key]}\n")
    else:
        _check_key_and_value(key, value)
        config_section[key] = value
        write_config(config_parser)


def _check_args_and_options(key: str, value: str, unset: bool) -> None:
    if unset:
        if value:
            error('Use "--unset" option to unset config or use "key" and "value" to set config')
        if not key:
            error('Use "--unset" option with "key"')
    if key not in {"editor", "timeout", "is_internal", "max_retries", ""}:
        error(f'The option "{key}" is not supported to configure currently.')


def _check_key_and_value(key: str, value: str) -> None:
    if key in {"timeout", "max_retries"}:
        if not value.isdigit():
            error(f'The option "{key}" need integer value.')
    elif key == "is_internal":
        if value.lower() not in {"true", "false", "0", "1"}:
            error('The option "is_internal" need True(1) or False(0) value.')
