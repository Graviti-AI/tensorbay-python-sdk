#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=import-outside-toplevel

"""Command-line interface.

Use ``gas <command>`` in terminal to operate on datasets.

Use ``gas auth`` to authenticate the accessKey of gas.

Use ``gas branch`` to list, create or delete branches.

Use ``gas commit`` to commit drafts.

Use ``gas config`` to configure the options when using gas CLI.

Use ``gas cp`` to copy local data to a remote path.

Use ``gas dataset`` to list, create or delete datasets.

Use ``gas draft`` to list or create drafts.

Use ``gas log`` to show commit logs.

Use ``gas ls`` to list data under the path.

Use ``gas rm`` to remove the remote data.

Use ``gas tag`` to list, create or delete tags.

"""

from functools import partial
from typing import Any, Dict, Iterable, Optional, Tuple

import click

from .. import __version__


class CustomCommand(click.Command):
    """Wrapper class of ``click.Command`` for CLI commands with custom help.

    Arguments:
        kwargs: The keyword arguments pass to ``click.Command``.

    """

    def __init__(self, **kwargs: Any) -> None:
        self.synopsis = kwargs.pop("synopsis", [])
        super().__init__(**kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Writes the custom help into the formatter if it exists.

        Override the original ``click.Command.format_help`` method by
        adding :meth:`CustomCommand.format_synopsis` to form custom help message.

        Arguments:
            ctx: The context of the command.
            formatter: The help formatter of the command.

        """
        formatter.width = 100
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_synopsis(formatter)  # Add synopsis in command help.
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_synopsis(self, formatter: click.HelpFormatter) -> None:
        """Wirte the synopsis to the formatter if exist.

        Arguments:
            formatter: The help formatter of the command.

        """
        if not self.synopsis:
            return

        with formatter.section("Synopsis"):
            for example in self.synopsis:
                formatter.write_text(example)


class DeprecatedCommand(CustomCommand):
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
    """You can use ``gas <command>`` to operate on your datasets.\f

    Arguments:
        ctx: The context to be passed as the first argument.
        access_key: The accessKey of gas.
        url: The login URL.
        profile_name: The environment to login.
        debug: Debug mode flag.

    """  # noqa: D301,D415
    from .utility import _implement_cli

    _implement_cli(ctx, access_key, url, profile_name, debug)


command = partial(cli.command, cls=CustomCommand)


@command(
    synopsis=(
        "$ gas ls                                       # List all the datasets.",
        "$ gas ls tb:<dataset_name>                     # List segments of a dataset.",
        "$ gas ls tb:<dataset_name>:<segment_name>      # List files of a segment.",
    )
)
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


@command(
    synopsis=(
        "$ gas config [key]                # Show the config.",
        "$ gas config <key> <value>        # Set the config.",
        "$ gas config -u [key]             # Unset the config.",
    )
)
@click.argument("key", type=str, default="")
@click.argument("value", type=str, default="")
@click.option("-u", "--unset", is_flag=True, help="Unset the config option")
def config(key: str, value: str, unset: bool) -> None:
    """Configure the options when using gas CLI.\f

    Arguments:
        key: The option key.
        value: The option value.
        unset: Whether to unset the option.

    """  # noqa: D301,D415
    from .config import _implement_config

    _implement_config(key, value, unset)


@command(
    synopsis=(
        "$ gas dataset                                  # List all the datasets.",
        "$ gas dataset tb:<dataset_name>                # Create a dataset.",
        "$ gas dataset -d [-y] tb:<dataset_name>        # Delete a dataset.",
    )
)
@click.argument("tbrn", type=str, default="")
@click.option("-d", "--delete", "is_delete", is_flag=True, help="Delete TensorBay dataset")
@click.option("-y", "--yes", is_flag=True, help="Confirm to delete the dataset completely.")
@click.pass_obj
def dataset(obj: Dict[str, str], tbrn: str, is_delete: bool, yes: bool) -> None:
    """List, create or delete datasets.\f

    Arguments:
        obj: A dict including config information.
        tbrn: The tbrn of the dataset, like "tb:KITTI".
        is_delete: Whether to delete the TensorBay dataset.
        yes: Confirm to delete the dataset completely.

    """  # noqa: D301,D415
    from .dataset import _implement_dataset

    _implement_dataset(obj, tbrn, is_delete, yes)


@command(
    synopsis=(
        "$ gas draft -l tb:<dataset_name>                                # List drafts.",
        "$ gas draft tb:<dataset_name>[@<branch_name>] [-t <title>]      # Create a draft.",
    )
)
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
    """List or create drafts.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of the dataset.
        is_list: Whether to list the drafts.
        title: The title of the draft.

    """  # noqa: D301,D415
    from .draft import _implement_draft

    _implement_draft(obj, tbrn, is_list, title)


@command(
    synopsis=("$ gas commit tb:<dataset_name>#<draft_number> [-m <message>]      # Commit a draft.")
)
@click.argument("tbrn", type=str)
@click.option(
    "-m", "--message", type=str, multiple=True, default=(), help="The message of the commit."
)
@click.pass_obj
def commit(obj: Dict[str, str], tbrn: str, message: Tuple[str, ...]) -> None:
    """Commit drafts.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The path to commit a draft, like "tb:KITTI#1".
        message: The message of the commit.

    """  # noqa: D301,D415
    from .commit import _implement_commit

    _implement_commit(obj, tbrn, message)


@command(
    synopsis=(
        "# Upload a file.",
        "$ gas cp <local_path> tb:<dataset_name>#<draft_number>:<segment_name>[://<remote_path]",
        "",
        "# Upload files.",
        "$ gas cp <local_path1> [local_path2 ...] tb:<dataset_name>#<draft_number>:<segment_name>",
        "",
        "# Upload files in a folder.",
        "$ gas cp -r <local_folder> tb:<dataset_name>#<draft_number>:<segment_name>",
    )
)
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


@command(
    synopsis=(
        "# Remove a segment.",
        "$ gas rm -r tb:<dataset_name>#<draft_number>:<segment_name>",
        "",
        "# Remove a file.",
        "$ gas rm tb:<dataset_name>#<draft_number>:<segment_name>://<remote_path>",
    )
)
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


@command(
    synopsis=(
        "$ gas branch tb:<dataset_name> [--verbose]                      # List branches.",
        "$ gas branch tb:<dataset_name>[@<revision>] <branch_name>       # Create a branch.",
        "$ gas branch -d tb:<dataset_name>@<branch_name>                 # Delete a branch.",
    )
)
@click.argument("tbrn", type=str)
@click.argument("name", type=str, default="")
@click.option("-v", "--verbose", is_flag=True, help="Show short commit id and commit message.")
@click.option("-d", "--delete", "is_delete", is_flag=True, help="Delete the branch")
@click.pass_obj
def branch(obj: Dict[str, str], tbrn: str, name: str, verbose: bool, is_delete: bool) -> None:
    """List, create or delete branches.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of the dataset.
        name: The name of the branch to be created.
        verbose: Whether to show the short commit id and commit message.
        is_delete: Whether to delete the branch.

    """  # noqa: D301,D415
    from .branch import _implement_branch

    _implement_branch(obj, tbrn, name, verbose, is_delete)


@command(
    synopsis=(
        "$ gas tag tb:<dataset_name>                            # List tags.",
        "$ gas tag tb:<dataset_name>[@<revision>] <tag_name>    # Create a tag.",
        "$ gas tag -d tb:<dataset_name>@<tag_name>              # Delete a tag.",
    )
)
@click.argument("tbrn", type=str)
@click.argument("name", type=str, default="")
@click.option("-d", "--delete", "is_delete", is_flag=True, help="Delete the tag.")
@click.pass_obj
def tag(obj: Dict[str, str], tbrn: str, name: str, is_delete: bool) -> None:
    """List, create or delete tags.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of the dataset.
        name: The name of the tag.
        is_delete: Whether to delete the tag.

    """  # noqa: D301,D415
    from .tag import _implement_tag

    _implement_tag(obj, tbrn, name, is_delete)


@command(
    synopsis=(
        "$ gas log tb:<dataset_name>[@<revision>]               # Show commit logs.",
        "$ gas log -n <number> tb:<dataset_name>[@<revision>]   # Show up to <number> commit logs.",
        "$ gas log --oneline tb:<dataset_name>[@<revision>]     # Show oneline commit logs.",
    )
)
@click.argument("tbrn", type=str)
@click.option(
    "-n", "--max-count", type=int, default=None, help="Limit the max number of commits to be showed"
)
@click.option("--oneline", is_flag=True, help="Limit commit message to oneline")
@click.pass_obj
def log(
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
) -> None:
    """Show commit logs.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of a dataset.
        max_count: Max number of commits to show.
        oneline: Whether to show a commit message in oneline.

    """  # noqa: D301,D415
    from .log import _implement_log

    _implement_log(obj, tbrn, max_count, oneline)


@command(
    synopsis=(
        "$ gas auth                      # Interactive authentication.",
        "$ gas auth <AccessKey>          # Authenticate with AccessKey.",
        "$ gas auth -g [-a]              # Get the authentication info.",
        "$ gas auth -u [-a]              # Unset the authentication info.",
    )
)
@click.argument("arg1", type=str, default="", metavar="accessKey")
@click.argument("arg2", type=str, default="", metavar="")
@click.option("-g", "--get", is_flag=True, help="Get the accesskey of the profile")
@click.option("-u", "--unset", is_flag=True, help="Unset the accesskey of the profile")
@click.option("-a", "--all", "is_all", is_flag=True, help="All the auth info")
@click.pass_obj
def auth(  # pylint: disable=too-many-arguments
    obj: Dict[str, str], arg1: str, arg2: str, get: bool, unset: bool, is_all: bool
) -> None:
    """Authenticate the accessKey of gas.\f

    Arguments:
        obj: A dict contains config information.
        arg1: The accessKey or the url of gas for the authentication.
        arg2: The accessKey of gas for the authentication if arg1 is url.
        get: Whether to get the accesskey of the profile.
        unset: Whether to unset the accesskey of the profile.
        is_all: All the auth info or not.

    """  # noqa: D301,D415
    from .auth import _implement_auth

    _implement_auth(obj, arg1, arg2, get, unset, is_all)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
