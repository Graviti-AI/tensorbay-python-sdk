#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas config."""

from .utility import read_config, update_config, write_config


def _implement_config(arg1: str, arg2: str) -> None:
    update_config()
    config_parser = read_config()

    if "config" not in config_parser:
        config_parser.add_section("config")
    config_parser["config"][arg1] = arg2
    write_config(config_parser)
