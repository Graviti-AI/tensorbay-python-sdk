#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=import-outside-toplevel

"""Command-line interface.

Use 'gas' + COMMAND in terminal to operate on datasets.

Use 'gas config' to  configure environment.

Use 'gas ls' to list data.

Use 'gas draft' to operate a draft.

"""

from typing import Any, Dict, Iterable, Optional

import click

from .. import __version__


class DeprecatedCommand(click.Command):
    """Customized ``click.Command`` wrapper class for deprecated CLI commands.

    Arguments:
        args: The positional arguments pass to ``click.Command``.
        since: The version the function is deprecated.
        removed_in: The version the function will be removed in.
        substitute: The substitute command.
        kwargs: The keyword arguments pass to ``click.Command``.

    """

    def __init__(
        self,
        *args: Any,
        since: str,
        removed_in: Optional[str] = None,
        substitute: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        messages = [
            f'DeprecationWarning: The command "{self.name}" is deprecated since version {since}.'
        ]
        if removed_in:
            messages.append(f'It will be removed in version "{removed_in}".')
        if substitute:
            messages.append(f'Use "{substitute}" instead.')

        self.deprecated_message = " ".join(messages)

    def invoke(self, ctx: click.Context) -> Any:
        """This invokes the command to print the deprecated message.

        Arguments:
            ctx: The click Context.

        Returns:
            The invoke result of ``click.Command``.

        """
        click.secho(self.deprecated_message, fg="red", err=True)
        return super().invoke(ctx)


@click.group()
@click.version_option(__version__)
@click.option(
    "-k",
    "--key",
    "access_key",
    type=str,
    default="",
    help="The AccessKey to TensorBay (replace the AccessKey in config file).",
)
@click.option("-u", "--url", type=str, default="", help="The login url.", hidden=True)
@click.option(
    "-p",
    "--profile",
    "profile_name",
    type=str,
    default="default",
    help="Choose a profile from the config file to login.",
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


@cli.command(
    cls=DeprecatedCommand,
    hidden=True,
    since="v1.5.0",
    removed_in="v1.8.0",
    substitute="gas dataset tb:[dataset_name]",
)
@click.argument("name", type=str)
@click.pass_obj
def create(obj: Dict[str, str], name: str) -> None:
    """Create a dataset.\f

    Arguments:
        obj: A dict including config information.
        name: The name of the dataset to be created, like "tb:KITTI".

    """  # noqa: D301,D415
    from .dataset import _implement_dataset

    _implement_dataset(obj, name, is_delete=False, yes=False)


@cli.command(
    cls=DeprecatedCommand,
    hidden=True,
    since="v1.5.0",
    removed_in="v1.8.0",
    substitute="gas dataset -d tb:[dataset_name]",
)
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
    from .dataset import _implement_dataset

    _implement_dataset(obj, name, is_delete=True, yes=yes)


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
@click.argument("url", type=str, default="", metavar="")
@click.pass_obj
def config(obj: Dict[str, str], access_key: str, url: str) -> None:
    """Configure the accessKey of gas.\f

    Arguments:
        obj: A dict contains config information.
        access_key: The accessKey of gas to write into config file.
        url: The URL of gas to write into config file.

    """  # noqa: D301,D415
    from .config import _implement_config

    _implement_config(obj, access_key, url)


@cli.command()
@click.argument("tbrn", type=str, default="")
@click.option("-d", "--delete", "is_delete", is_flag=True, help="Delete TensorBay dataset")
@click.option("-y", "--yes", is_flag=True, help="Confirm to delete the dataset completely.")
@click.pass_obj
def dataset(obj: Dict[str, str], tbrn: str, is_delete: bool, yes: bool) -> None:
    """Work with TensorBay datasets\f

    Arguments:
        obj: A dict including config information.
        tbrn: The tbrn of the dataset, like "tb:KITTI".
        is_delete: Whether to delete the TensorBay dataset.
        yes: Confirm to delete the dataset completely.

    """  # noqa: D301,D415
    from .dataset import _implement_dataset

    _implement_dataset(obj, tbrn, is_delete, yes)


@cli.command()
@click.argument("tbrn", type=str)
@click.option("-l", "--list", "is_list", is_flag=True, help="List the drafts.")
@click.option("-t", "--title", type=str, default="", help="The title of the draft.")
@click.pass_obj
def draft(
    obj: Dict[str, str],
    tbrn: str,
    is_list: bool,
    title: str,
) -> None:
    """Work with draft.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of the dataset.
        is_list: Whether to list the drafts.
        title: The title of the draft.

    """  # noqa: D301,D415
    from .draft import _implement_draft

    _implement_draft(obj, tbrn, is_list, title)


@cli.command()
@click.argument("tbrn", type=str)
@click.option("-m", "--message", type=str, required=True, help="The message of the commit.")
@click.pass_obj
def commit(obj: Dict[str, str], tbrn: str, message: str) -> None:
    """Work with commit.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The path to commit a draft, like "tb:KITTI#1".
        message: The message of the commit.

    """  # noqa: D301,D415
    from .commit import _implement_commit

    _implement_commit(obj, tbrn, message)


@cli.command()
@click.argument("local_paths", type=str, nargs=-1)
@click.argument("tbrn", type=str, nargs=1)
@click.option(
    "-r", "--recursive", "is_recursive", is_flag=True, help="Copy directories recursively."
)
@click.option("-j", "--jobs", type=int, default=1, help="The number of threads.")
@click.option(
    "-s",
    "--skip",
    "skip_uploaded_files",
    is_flag=True,
    help="Whether to skip the uploaded files.",
)
@click.pass_obj
def cp(  # pylint: disable=invalid-name, too-many-arguments
    obj: Dict[str, str],
    local_paths: Iterable[str],
    tbrn: str,
    is_recursive: bool,
    jobs: int,
    skip_uploaded_files: bool,
) -> None:
    """Copy local data to a remote path.\f

    Arguments:
        obj: A dict contains config information.
        local_paths: An iterable of local paths contains data to be uploaded.
        tbrn: The path to save the uploaded data, like "tb:KITTI:seg1".
        is_recursive: Whether copy directories recursively.
        jobs: Number of threads to upload data.
        skip_uploaded_files: Whether skip the uploaded files.

    """  # noqa: D301,D415
    from .cp import _implement_cp

    _implement_cp(obj, local_paths, tbrn, is_recursive, jobs, skip_uploaded_files)


@cli.command()
@click.argument("tbrn", type=str)
@click.option(
    "-r", "--recursive", "is_recursive", is_flag=True, help="Remove directories recursively."
)
@click.pass_obj
def rm(  # pylint: disable=invalid-name, too-many-arguments
    obj: Dict[str, str], tbrn: str, is_recursive: bool
) -> None:
    """Remove the remote data.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The path to be removed, like "tb:KITTI#1".
        is_recursive: Whether remove directories recursively.

    """  # noqa: D301,D415
    from .rm import _implement_rm

    _implement_rm(obj, tbrn, is_recursive)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
