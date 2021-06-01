#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

from typing import Dict

import click

from .utility import error, form_profile_value, read_config, update_config, write_config

_INDENT = " " * 4


def _implement_config(obj: Dict[str, str], arg1: str, arg2: str) -> None:
    update_config()
    config_parser = read_config()

    if not arg1:
        for profile_name in config_parser.sections():
            click.echo(f"[{profile_name}]")
            for key, value in config_parser[profile_name].items():
                formatted_value = value.replace("\n", f"\n{_INDENT * 2}")
                click.echo(f"{_INDENT}{key} = {formatted_value}\n")
        return

    if arg1.startswith(("Accesskey-", "ACCESSKEY-")):
        profile_name = obj["profile_name"]
        if profile_name == "config":
            error("Name 'config' is preserved for gas basic config")

        if not config_parser.has_section("profiles"):
            config_parser.add_section("profiles")
        config_parser["profiles"][profile_name] = form_profile_value(arg1, arg2)

    elif arg1 == "editor":
        if not arg2:
            error("Missing editor name")

        if not config_parser.has_section("config"):
            config_parser.add_section("config")
        config_parser["config"]["editor"] = arg2
    else:
        error("Wrong accesskey format")

    write_config(config_parser)
