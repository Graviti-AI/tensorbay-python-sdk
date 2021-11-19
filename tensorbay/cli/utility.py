#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay gas CLI utility functions."""

import logging
import os
import sys
from collections import OrderedDict
from configparser import ConfigParser, SectionProxy
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple, TypeVar, overload

import click
from typing_extensions import Literal, NoReturn

from tensorbay.cli.tbrn import TBRN
from tensorbay.client import GAS
from tensorbay.client import config as client_config
from tensorbay.client.dataset import DatasetClient, FusionDatasetClient
from tensorbay.client.gas import DatasetClientType
from tensorbay.client.log import dump_request_and_response
from tensorbay.client.requests import logger
from tensorbay.client.struct import Branch, Tag
from tensorbay.exception import InternalServerError, TensorBayException

_Callable = TypeVar("_Callable", bound=Callable[..., None])
_T = TypeVar("_T", Tag, Branch)
INDENT = " " * 4

_SORT_KEYS = {
    "name": lambda x: x.name,
    "commit_date": lambda x: (x.committer.date, x.name),
}


class ContextInfo:
    """This class contains command context."""

    def __init__(self, access_key: str, url: str, profile_name: str):
        self.access_key = access_key
        self.url = url
        self.profile_name = profile_name

        config_filepath = self._get_config_filepath()

        config_parser = ConfigParser(dict_type=OrderedDict)
        config_parser.read(config_filepath)
        self.config_parser = config_parser

    @staticmethod
    def _get_config_filepath() -> str:
        """Get the path of the config file.

        Returns:
            The path of the config file.

        """
        return os.path.join(os.path.expanduser("~"), ".gasconfig")

    @staticmethod
    def _is_updated(profile_section: SectionProxy) -> bool:
        return "\n" in profile_section.get("accesskey", "\n")

    @staticmethod
    def _parse_profile_info(profile_info: str) -> Tuple[str, str]:
        """Parse the profile information to get accessKey and URL.

        Arguments:
            profile_info: The profile information read from the config file.

        Returns:
            A tuple containing the accessKey and the url of profile_name read from the config file.

        """
        values = profile_info.split("\n")
        if len(values) == 2:
            return values[1], ""
        return values[1], values[2]

    def _set_request_config(self) -> None:
        """Configure request related parameters."""
        config_parser = self.config_parser
        client_config._x_source = "PYTHON-CLI"  # pylint: disable=protected-access
        if config_parser.has_section("config"):
            config_section = config_parser["config"]
            if "timeout" in config_section:
                client_config.timeout = config_section.getint("timeout")
            if "is_internal" in config_section:
                client_config.is_internal = config_section.getboolean("is_internal")
            if "max_retries" in config_section:
                client_config.max_retries = config_section.getint("max_retries")

    def generate_profiles(self) -> Iterable[Tuple[str, str, str]]:
        """Get all profiles and corresponding profile information.

        Yields:
            A tuple containing profile name and the corresponding accesskey and url read from
            the config file.

        """
        try:
            profiles = self.config_parser["profiles"]
        except KeyError:
            return
        yield from ((k, *self._parse_profile_info(v)) for k, v in profiles.items())

    def get_gas(self, access_key: Optional[str] = None, url: Optional[str] = None) -> GAS:
        """Load an object of :class:`~tensorbay.client.gas.GAS`.

        Read accessKey and URL from the appointed profile_name and login gas.

        Arguments:
            access_key: The accessKey of gas.
            url: The login URL.

        Returns:
            Gas client logged in with accessKey and URL.

        """
        self._set_request_config()

        if access_key is None:
            access_key, url = self.access_key, self.url

        if not access_key and not url:
            access_key, url = self.read_profile()

        if not access_key:
            error(
                "AccessKey should be appointed. Please visit and login to the "
                "TensorBay website to generate your AccessKey"
            )

        return GAS(access_key, url)  # type:ignore[arg-type]

    def read_profile(self) -> Tuple[str, str]:
        """Read accessKey and URL from the config file.

        Returns:
            A tuple containing the accessKey and the url of profile_name read from the config file.

        """
        profile_name = self.profile_name
        config_parser = self.config_parser
        if not config_parser.has_option("profiles", profile_name):
            error(
                f"{profile_name} does not exist"
                f"\n\nPlease use 'gas -p {profile_name} auth [accessKey]' to create profile"
            )
        return self._parse_profile_info(config_parser["profiles"][profile_name])

    def update_config(self) -> None:
        """Update the config parser to the new format."""
        config_parser = self.config_parser
        old_sections = config_parser.sections()

        if not old_sections or old_sections == ["config"]:
            return

        if (old_sections in (["config", "profiles"], ["profiles"])) and self._is_updated(
            config_parser["profiles"]
        ):
            return

        new_config_parser = ConfigParser(dict_type=OrderedDict)
        new_config_parser.add_section("profiles")
        for section_name, section_value in config_parser.items():
            if section_name == "DEFAULT":
                continue

            if section_name == "config":
                new_config_parser.add_section("config")
                new_config_parser["config"] = config_parser["config"]

            elif section_name == "profiles" and self._is_updated(section_value):
                new_config_parser["profiles"].update(section_value)

            else:
                new_config_parser["profiles"][section_name] = form_profile_value(**section_value)
        self.config_parser = new_config_parser
        self.write_config(show_message=False)

    def write_config(self, show_message: bool = True) -> None:
        """Write the config parser to the config file.

        Arguments:
            show_message: Whether to show the message.

        """
        # pylint: disable=protected-access
        config_parser = self.config_parser
        if config_parser.has_section("config"):
            config_parser._sections.move_to_end("config", last=False)  # type: ignore[attr-defined]
        if config_parser.has_section("profiles") and config_parser.has_option(
            "profiles", "default"
        ):
            config_parser._sections["profiles"].move_to_end(  # type: ignore[attr-defined]
                "default", last=False
            )

        config_file = self._get_config_filepath()
        with open(config_file, "w", encoding="utf-8") as fp:
            config_parser.write(fp)
        if show_message:
            click.echo(f'Success!\nConfiguration has been written into: "{config_file}"')


def _implement_cli(
    ctx: click.Context, access_key: str, url: str, profile_name: str, debug: bool
) -> None:
    ctx.obj = ContextInfo(access_key, url, profile_name)
    ctx.obj.update_config()

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logger.disabled = True


@overload
def get_dataset_client(
    gas: GAS, tbrn_info: TBRN, is_fusion: Literal[None] = None
) -> DatasetClientType:
    ...


@overload
def get_dataset_client(gas: GAS, tbrn_info: TBRN, is_fusion: Literal[False]) -> DatasetClient:
    ...


@overload
def get_dataset_client(gas: GAS, tbrn_info: TBRN, is_fusion: Literal[True]) -> FusionDatasetClient:
    ...


@overload
def get_dataset_client(
    gas: GAS, tbrn_info: TBRN, is_fusion: Optional[bool] = None
) -> DatasetClientType:
    ...


def get_dataset_client(
    gas: GAS, tbrn_info: TBRN, is_fusion: Optional[bool] = None
) -> DatasetClientType:
    """Get the dataset client with any type and its version info.

    Arguments:
        gas: The gas client.
        tbrn_info: The tbrn of the resource.
        is_fusion: Whether the dataset is a fusion dataset, True for fusion dataset.

    Returns:
        The dataset client and its version info.

    """
    dataset_client = (
        gas._get_dataset_with_any_type(tbrn_info.dataset_name)  # pylint: disable=protected-access
        if is_fusion is None
        else gas.get_dataset(tbrn_info.dataset_name, is_fusion)
    )
    if tbrn_info.is_draft:
        dataset_client.checkout(draft_number=tbrn_info.draft_number)
    elif tbrn_info.revision is not None:
        dataset_client.checkout(revision=tbrn_info.revision)
    return dataset_client


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


def _edit_input(hint: str, config_parser: ConfigParser) -> Tuple[str, str]:
    """Edit information input from the editor.

    Arguments:
        hint: The hint to be added in the temp file opened by the editor.
        config_parser: The config parser read from the context object.

    Returns:
        The extracted title and the description.

    """
    editor = config_parser["config"].get("editor") if config_parser.has_section("config") else None
    input_info = click.edit(hint, editor=editor, require_save=False)
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


def is_accesskey(arg: str) -> bool:
    """Determine whether the string is an AccessKey.

    Arguments:
        arg: The string needed to be judged.

    Returns:
        Whether the string is an AccessKey.

    """
    return arg.startswith(("Accesskey-", "ACCESSKEY-")) and len(arg) == 42


def shorten(origin: str) -> str:
    """Return the first 7 characters of the original string.

    Arguments:
        origin: The string needed to be shortened.

    Returns:
        A string of length 7.

    """
    return origin[:7]


def format_hint(title: str, description: str, original_hint: str) -> str:
    """Generate complete hint message.

    Arguments:
        title: The title of the draft to edit or commit.
        description: The description of the draft to edit or commit.
        original_hint: The original hint message.

    Returns:
        The complete hint message.

    """
    hint: Tuple[str, ...] = (title,)
    if description:
        hint += ("", description)
    hint += (original_hint,)
    return "\n".join(hint)


def edit_message(
    message: Tuple[str, ...], hint_message: str, config_parser: ConfigParser
) -> Tuple[str, str]:
    """Edit draft information.

    Arguments:
        message: The message given in the CLI.
        hint_message: The hint message to show on the pop-up editor.
        config_parser: The config parser read from the context object.

    Returns:
        The extracted title and the description.

    """
    if message:
        title, description = message[0], "\n".join(message[1:])
    else:
        title, description = _edit_input(hint_message, config_parser)

    return title, description


def echo_response(err: InternalServerError) -> None:
    """Log request and response when InternalServerError happens.

    Arguments:
        err: The InternalServerError raised from the CLI.

    """
    if logger.disabled:
        click.echo(dump_request_and_response(err.response))


def exception_handler(func: _Callable) -> _Callable:
    """Decorator for CLI functions to catch custom exceptions.

    Arguments:
        func: The CLI function needs to be decorated.

    Returns:
        The CLI function with exception catching procedure.

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except InternalServerError as err:
            echo_response(err)
            raise
        except TensorBayException as err:
            error(str(err))

    return wrapper  # type: ignore[return-value]


def sort_branches_or_tags(sort_key: str, target: Sequence[_T]) -> Sequence[_T]:
    """Check whether the sort_key is valid and sort the target.

    Arguments:
        sort_key: The key to sort on.
        target: The target to be sorted.

    Returns:
        The sorted target.

    """
    key, reverse = (sort_key, False) if sort_key[0] != "-" else (sort_key[1:], True)
    if key not in _SORT_KEYS:
        error(
            'The "--sort" option must be "name" or "commit_date" with an optional "-" before them'
        )
    if not reverse and sort_key == "name":
        return target
    return sorted(target, key=_SORT_KEYS[key], reverse=reverse)
