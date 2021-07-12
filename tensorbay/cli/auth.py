#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas auth."""


from configparser import ConfigParser
from textwrap import indent
from typing import Dict, Optional
from urllib.parse import urljoin

import click

from .utility import (
    error,
    form_profile_value,
    is_accesskey,
    read_config,
    update_config,
    write_config,
)

INDENT = " " * 4


def _implement_auth(  # pylint: disable=too-many-arguments
    obj: Dict[str, str], arg1: str, arg2: str, get: bool, unset: bool, is_all: bool
) -> None:
    _check_args_and_options(arg1, arg2, get, unset, is_all)
    update_config()
    config_parser = read_config()

    if get:
        _get_auth(obj, config_parser, is_all)
        return

    if unset:
        _unset_auth(obj, config_parser, is_all)
        return

    if not arg1 and not arg2:
        arg1 = _interactive_auth()

    elif is_accesskey(arg1):
        if _is_gas_url(arg2):
            error('Please use "gas auth [url] [accessKey]" to specify the url and accessKey')
        if arg2:
            error(f'Redundant argument "{arg2}"')

    elif _is_gas_url(arg1):
        if not arg2:
            arg2 = _interactive_auth(arg1)
        elif not is_accesskey(arg2):
            error("Wrong accesskey format")
    else:
        error(f'Invalid argument "{arg1}"')

    _update_profile(config_parser, obj["profile_name"], arg1, arg2)
    write_config(config_parser)


def _get_auth(obj: Dict[str, str], config_parser: ConfigParser, is_all: bool) -> None:
    if is_all:
        for key, value in config_parser["profiles"].items():
            _echo_formatted_profile(key, value)
        return

    profile_name = obj["profile_name"]
    _echo_formatted_profile(profile_name, config_parser["profiles"][profile_name])


def _unset_auth(obj: Dict[str, str], config_parser: ConfigParser, is_all: bool) -> None:
    if is_all:
        config_parser.remove_section("profiles")
    else:
        config_parser.remove_option("profiles", obj["profile_name"])
    write_config(config_parser, show_message=False)
    click.echo("Unset successfully")


def _interactive_auth(url: Optional[str] = None) -> str:
    click.secho(
        "Please visit and login to the TensorBay website to generate your AccessKey", bold=True
    )
    click.secho(
        "Note: TensorBay has multi-regional websites, "
        "please visit the corresponding website based on your location for better experience\n",
        fg="bright_cyan",
    )

    if url:
        developer_url = click.style(urljoin(url, "/tensorbay/developer"), underline=True)
        click.echo(f" > {developer_url}\n")
    else:
        url_cn = click.style("https://gas.graviti.cn/tensorbay/developer", underline=True)
        url_com = click.style("https://gas.graviti.com/tensorbay/developer", underline=True)
        click.echo(f" > {url_com} (Global site)")
        click.echo(f" > {url_cn} (Chinese site)\n")

    access_key = click.prompt(click.style("Paste your AccessKey here", bold=True)).strip()
    if not is_accesskey(access_key):
        error("Wrong accesskey format")
    return access_key  # type: ignore[no-any-return]


def _is_gas_url(arg: str) -> bool:
    return arg.startswith("https://gas.")


def _update_profile(config_parser: ConfigParser, profile_name: str, arg1: str, arg2: str) -> None:
    if not config_parser.has_section("profiles"):
        config_parser.add_section("profiles")

    config_parser["profiles"][profile_name] = (
        form_profile_value(arg1) if not arg2 else form_profile_value(arg2, arg1)
    )


def _check_args_and_options(arg1: str, arg2: str, get: bool, unset: bool, is_all: bool) -> None:
    if is_all and not (get or unset):
        error('Use "--all" option with "--get" or "--unset" option')

    if get and unset:
        error('Use either "--get" or "--unset"')

    if (get or unset) and (arg1 or arg2):
        error("Option requires 0 arguments")


def _echo_formatted_profile(name: str, value: str) -> None:
    formatted_value = indent(value, INDENT)
    click.echo(f"{name} = {formatted_value}\n")
