#!/usr/bin/env python3
#
# Copyright 2021 Graviti. All Rights Reserved.
#
# pylint: disable=import-outside-toplevel

"""Command-line interface.

Use 'gas' + COMMAND in terminal to operate on datasets.

Use 'gas config' to  configure environment.

Use 'gas create' to create a dataset.

Use 'gas delete' to delete a dataset.

Use 'gas ls' to list data.

"""

from typing import Dict

import click

from .. import __version__


@click.group()
@click.version_option(__version__)
@click.option("-k", "--key", "access_key", type=str, default="", help="The accessKey of gas.")
@click.option("-u", "--url", type=str, default="", help="The login url.", hidden=True)
@click.option(
    "-p",
    "--profile",
    "profile_name",
    type=str,
    default="default",
    help="The environment to login.",
)
@click.option("-d", "--debug", is_flag=True, help="Debug mode.")
@click.pass_context
def cli(ctx: click.Context, access_key: str, url: str, profile_name: str, debug: bool) -> None:
    """You can use 'gas' + COMMAND to operate on your dataset.\f

    Arguments:
        ctx: The context to be passed as the first argument.
        access_key: The accessKey of gas.
        url: The login URL.
        profile_name: The environment to login.
        debug: Debug mode flag.

    """  # noqa: D301,D415
    from .utility import _implement_cli

    _implement_cli(ctx, access_key, url, profile_name, debug)


@cli.command()
@click.argument("name", type=str)
@click.pass_obj
def create(obj: Dict[str, str], name: str) -> None:
    """Create a dataset.\f

    Arguments:
        obj: A dict including config information.
        name: The name of the dataset to be created, like "tb:KITTI".

    """  # noqa: D301,D415
    from .create import _implement_create

    _implement_create(obj, name)


@cli.command()
@click.argument("name", type=str)
@click.option("-y", "--yes", is_flag=True, help="Confirm to delete the dataset completely.")
@click.pass_obj
def delete(obj: Dict[str, str], name: str, yes: bool) -> None:
    """Delete a dataset.\f

    Arguments:
        obj: A dict including config info.
        name: The name of the dataset to be deleted, like "tb:KITTI".
        yes: Confirm to delete the dataset completely.

    """  # noqa: D301,D415
    from .delete import _implement_delete

    _implement_delete(obj, name, yes)


@cli.command()
@click.argument("tbrn", type=str, default="")
@click.option(
    "-a", "--all", "list_all_files", is_flag=True, help="List all files under the segment."
)
@click.pass_obj
def ls(  # pylint: disable=invalid-name
    obj: Dict[str, str], tbrn: str, list_all_files: bool
) -> None:
    """List data under the path. If path is empty, list the names of all datasets.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: Path to be listed, like "tb:KITTI:seg1". If empty, list names of all datasets.
        list_all_files: If true, list all files under the segment.

    """  # noqa: D301,D415
    from .ls import _implement_ls

    _implement_ls(obj, tbrn, list_all_files)


@cli.command()
@click.argument("access_key", type=str, default="")
@click.argument("url", type=str, default="")
@click.pass_obj
def config(obj: Dict[str, str], access_key: str, url: str) -> None:
    """Configure the accessKey (and URL) of gas.\f

    Arguments:
        obj: A dict contains config information.
        access_key: The accessKey of gas to write into config file.
        url: The URL of gas to write into config file.

    """  # noqa: D301,D415
    from .config import _implement_config

    _implement_config(obj, access_key, url)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
