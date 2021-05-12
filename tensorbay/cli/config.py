#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

import sys
from configparser import ConfigParser
from typing import Dict

import click

from .utility import get_config_filepath


def _implement_config(obj: Dict[str, str], access_key: str, url: str) -> None:
    config_file = get_config_filepath()
    config_parser = ConfigParser()
    config_parser.read(config_file)

    if not access_key:
        for profile_name in config_parser.sections():
            click.echo(f"[{profile_name}]")
            for key, value in config_parser[profile_name].items():
                click.echo(f"{key} = {value}")
        return

    if not access_key.startswith(("Accesskey-", "ACCESSKEY-")):
        click.echo("Error: Wrong accesskey format", err=True)
        sys.exit(1)

    profile_name = obj["profile_name"]
    if profile_name == "config":
        click.echo("Error: name 'config' is preserved for gas basic config", err=True)
        sys.exit(1)

    if profile_name not in config_parser:
        config_parser.add_section(profile_name)

    config_parser[profile_name]["accessKey"] = access_key
    if url:
        config_parser[profile_name]["url"] = url
    else:
        config_parser.remove_option(profile_name, "url")

    with open(config_file, "w") as fp:
        config_parser.write(fp)

    click.echo(f"Success!\nConfiguration has been written into: {config_file}")
