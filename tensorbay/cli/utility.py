#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Graviti Tensorbay gas CLI utility functions."""

import logging
import os
import sys
from collections import OrderedDict
from configparser import ConfigParser, SectionProxy
from typing import NoReturn, Optional, Tuple, overload

import click
from typing_extensions import Literal

from ..client import GAS
from ..client import config as client_config
from ..client.dataset import DatasetClient, FusionDatasetClient
from ..client.gas import DatasetClientType
from .tbrn import TBRN


def _implement_cli(
    ctx: click.Context, access_key: str, url: str, profile_name: str, debug: bool
) -> None:
    ctx.obj = {
        "access_key": access_key,
        "url": url,
        "profile_name": profile_name,
    }
    client_config._x_source = "PYTHON-CLI"  # pylint: disable=protected-access

    if debug:
        logging.basicConfig(level=logging.DEBUG)


def _get_config_filepath() -> str:
    """Get the path of the config file.

    Returns:
        The path of the config file.

    """
    home = "USERPROFILE" if os.name == "nt" else "HOME"
    return os.path.join(os.environ[home], ".gasconfig")


def _read_profile(profile_name: str) -> Tuple[str, str]:
    """Read accessKey and URL from the config file.

    Arguments:
        profile_name: The environment to login.

    Returns:
        A tuple containing the accessKey and the url of profile_name read from the config file.

    """
    config_filepath = _get_config_filepath()
    if not os.path.exists(config_filepath):
        error(
            f"{config_filepath} not exist"
            "\n\nPlease use 'gas config <accessKey>' to create config file"
        )

    update_config()
    config_parser = read_config(config_filepath)
    values = config_parser["profiles"][profile_name].split("\n")
    if len(values) == 2:
        return values[1], ""
    return values[1], values[2]


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
        access_key, url = _read_profile(profile_name)

    if not access_key:
        error("AccessKey should be appointed")

    return GAS(access_key, url)


@overload
def get_dataset_client(gas: GAS, info: TBRN, is_fusion: Literal[None] = None) -> DatasetClientType:
    ...


@overload
def get_dataset_client(gas: GAS, info: TBRN, is_fusion: Literal[False]) -> DatasetClient:
    ...


@overload
def get_dataset_client(gas: GAS, info: TBRN, is_fusion: Literal[True]) -> FusionDatasetClient:
    ...


@overload
def get_dataset_client(gas: GAS, info: TBRN, is_fusion: Optional[bool] = None) -> DatasetClientType:
    ...


def get_dataset_client(gas: GAS, info: TBRN, is_fusion: Optional[bool] = None) -> DatasetClientType:
    """Get the dataset client with any type and its version info.

    Arguments:
        gas: The gas client.
        info: The tbrn of the resource.
        is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.

    Returns:
        The dataset client and its version info.

    """
    dataset_client = (
        gas._get_dataset_with_any_type(info.dataset_name)  # pylint: disable=protected-access
        if is_fusion is None
        else gas.get_dataset(info.dataset_name, is_fusion)
    )
    if info.is_draft:
        dataset_client.checkout(draft_number=info.draft_number)
    elif info.revision is not None:
        dataset_client.checkout(revision=info.revision)
    return dataset_client


def edit_input(hint: str) -> Tuple[str, str]:
    """Edit information input from the editor.

    Arguments:
        hint: The hint to be added in the temp file opened by the editor.

    Returns:
        The extracted title and the description.

    """
    config_parser = read_config()

    editor = config_parser["config"].get("editor") if config_parser.has_section("config") else None
    input_info = click.edit(hint, editor=editor)
    return _clean_up(input_info)


def _clean_up(editor_input: Optional[str]) -> Tuple[str, str]:
    """Clean up the information from the editor input.

    Arguments:
        editor_input: The editor input.

    Returns:
        The extracted title and the description.

    """
    if not editor_input:
        return "", ""

    cleaned_up_lines = []
    for line in editor_input.splitlines():
        if line and not line.startswith("#"):
            cleaned_up_lines.append(line.rstrip())

    if not cleaned_up_lines:
        return "", ""
    return cleaned_up_lines[0].lstrip(), "\n".join(cleaned_up_lines[1:])


def error(message: str) -> NoReturn:
    """Print the error message and exit the program.

    Arguments:
        message: The error message to echo.

    """
    click.secho(f"ERROR: {message}", err=True, fg="red")
    sys.exit(1)


def update_config() -> None:
    """Update the config file to the new format."""
    old_config_parser = read_config()
    old_sections = old_config_parser.sections()

    if not old_sections or old_sections == ["config"]:
        return

    if (old_sections in (["config", "profiles"], ["profiles"])) and _is_updated(
        old_config_parser["profiles"]
    ):
        return

    new_config_parser = ConfigParser(dict_type=OrderedDict)
    new_config_parser.add_section("profiles")
    for section_name, section_value in old_config_parser.items():
        if section_name == "DEFAULT":
            continue

        if section_name == "config":
            new_config_parser.add_section("config")
            new_config_parser["config"] = old_config_parser["config"]

        elif section_name == "profiles" and _is_updated(section_value):
            new_config_parser["profiles"].update(section_value)

        else:
            new_config_parser["profiles"][section_name] = form_profile_value(**section_value)

    write_config(new_config_parser, show_message=False)


def _is_updated(profile_section: SectionProxy) -> bool:
    return "\n" in profile_section.get("accesskey", "\n")


def form_profile_value(accesskey: str, url: Optional[str] = None) -> str:
    """Form the profile value with accesskey (and url).

    Arguments:
        accesskey: The accesskey to TensorBay.
        url: The TensorBay url.

    Returns:
        The formed profile value.

    """
    values = ["", accesskey]
    if url:
        values.append(url)
    return "\n".join(values)


def read_config(config_filepath: Optional[str] = None) -> ConfigParser:
    """Write the config from the config file.

    Arguments:
        config_filepath: The path of the config file to read.

    Returns:
        The config parser read from the config file.

    """
    if not config_filepath:
        config_filepath = _get_config_filepath()
    config_parser = ConfigParser(dict_type=OrderedDict)
    config_parser.read(config_filepath)
    return config_parser


def write_config(config_parser: ConfigParser, show_message: bool = True) -> None:
    """Write the config parser to the config file.

    Arguments:
        config_parser: The config parser to write to the file.
        show_message: Whether to show the message.

    """
    # pylint: disable=protected-access
    if config_parser.has_section("config"):
        config_parser._sections.move_to_end("config", last=False)  # type: ignore[attr-defined]
    if config_parser.has_section("profiles") and config_parser.has_option("profiles", "default"):
        config_parser._sections["profiles"].move_to_end(  # type: ignore[attr-defined]
            "default", last=False
        )

    config_file = _get_config_filepath()
    with open(config_file, "w") as fp:
        config_parser.write(fp)
    if show_message:
        click.echo(f'Success!\nConfiguration has been written into: "{config_file}"')


def is_accesskey(arg: str) -> bool:
    """Determine whether the string is an AccessKey.

    Arguments:
        arg: The string needed to be judged.

    Returns:
        Whether the string is an AccessKey.

    """
    return arg.startswith(("Accesskey-", "ACCESSKEY-")) and len(arg) == 42
