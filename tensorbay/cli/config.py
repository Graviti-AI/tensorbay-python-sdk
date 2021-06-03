#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

from configparser import ConfigParser
from typing import Dict

import click

from .utility import error, get_config_filepath


def _implement_config(obj: Dict[str, str], arg1: str, arg2: str) -> None:
    config_file = get_config_filepath()
    config_parser = ConfigParser()
    config_parser.read(config_file)

    if not arg1:
        for profile_name in config_parser.sections():
            click.echo(f"[{profile_name}]")
            for key, value in config_parser[profile_name].items():
                click.echo(f"{key} = {value}")
        return

    if arg1.startswith(("Accesskey-", "ACCESSKEY-")):
        profile_name = obj["profile_name"]
        if profile_name == "config":
            error("Name 'config' is preserved for gas basic config")

        if profile_name not in config_parser:
            config_parser.add_section(profile_name)

        config_parser[profile_name]["accessKey"] = arg1
        if arg2:
            config_parser[profile_name]["url"] = arg2
        else:
            config_parser.remove_option(profile_name, "url")
    elif arg1 == "editor":
        if not arg2:
            error("Missing editor name")

        if "config" not in config_parser:
            config_parser.add_section("config")
        config_parser["config"]["editor"] = arg2
    else:
        error("Wrong accesskey format")

    with open(config_file, "w") as fp:
        config_parser.write(fp)

    click.echo(f"Success!\nConfiguration has been written into: {config_file}")
