#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas auth."""


from configparser import ConfigParser
from typing import Dict

from .utility import error, form_profile_value, read_config, update_config, write_config


def _implement_auth(obj: Dict[str, str], arg1: str, arg2: str) -> None:
    update_config()
    config_parser = read_config()

    if not arg1 and not arg2:
        error("Require accessKey to authenticate Tensorbay account")

    if _is_accesskey(arg1):
        if _is_url(arg2):
            error('Please use "gas auth [url] [accessKey]" to specify the url and accessKey')
        if arg2:
            error(f'Redundant argument "{arg2}"')

    elif _is_url(arg1):
        if not arg2:
            error("Require accessKey to authenticate Tensorbay account")
        if not _is_accesskey(arg2):
            error("Wrong accesskey format")
    else:
        error(f'Invalid argument "{arg1}"')

    _update_profile(config_parser, obj["profile_name"], arg1, arg2)
    write_config(config_parser)


def _is_accesskey(arg: str) -> bool:
    return arg.startswith(("Accesskey-", "ACCESSKEY-")) and len(arg) == 42


def _is_url(arg: str) -> bool:
    return arg.startswith("https://")


def _update_profile(config_parser: ConfigParser, profile_name: str, arg1: str, arg2: str) -> None:
    if not config_parser.has_section("profiles"):
        config_parser.add_section("profiles")

    config_parser["profiles"][profile_name] = (
        form_profile_value(arg1) if not arg2 else form_profile_value(arg2, arg1)
    )
