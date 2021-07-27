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
from typing import Dict, Iterable, Optional, Tuple

import click

from .. import __version__
from .custom import CustomCommand, DeprecatedOption, DeprecatedOptionsCommand


@click.group(context_settings={"help_option_names": ("-h", "--help")})
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
@click.option("-l", "show_total_num", is_flag=True, help="Show the total number of resources")
@click.pass_obj
def ls(  # pylint: disable=invalid-name
    obj: Dict[str, str], tbrn: str, list_all_files: bool, show_total_num: bool
) -> None:
    """List data under the path. If path is empty, list the names of all datasets.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: Path to be listed, like "tb:KITTI:seg1". If empty, list names of all datasets.
        list_all_files: If true, list all files under the segment.
        show_total_num: If true, show the total number of resources.

    """  # noqa: D301,D415
    from .ls import _implement_ls

    _implement_ls(obj, tbrn, list_all_files, show_total_num)


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
    cls=DeprecatedOptionsCommand,
    synopsis=(
        "$ gas draft -l tb:<dataset_name>                                # List drafts.",
        "$ gas draft tb:<dataset_name>[@<branch_name>] [-m <title>]      # Create a draft.",
    ),
)
@click.argument("tbrn", type=str)
@click.option("-l", "--list", "is_list", is_flag=True, help="List the drafts.")
@click.option("-e", "--edit", is_flag=True, help="Edit the draft's title and description.")
@click.option("-c", "--close", is_flag=True, help="Close the draft.")
@click.option(
    "-m",
    "--message",
    "-t",
    "--title",
    type=str,
    multiple=True,
    default=(),
    help="The title of the draft.",
    deprecated=("-t", "--title"),
    preferred="-m",
    since="v1.8.0",
    removed_in="v1.10.0",
    cls=DeprecatedOption,
)
@click.pass_obj
def draft(  # pylint: disable=too-many-arguments
    obj: Dict[str, str],
    tbrn: str,
    is_list: bool,
    edit: bool,
    close: bool,
    message: Tuple[str, ...],
) -> None:
    """List or create drafts.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of the dataset.
        is_list: Whether to list the drafts.
        edit: Whether to edit the draft's title and description.
        close: Whether to close the draft.
        message: The message of the draft.

    """  # noqa: D301,D415
    from .draft import _implement_draft

    _implement_draft(obj, tbrn, is_list, edit, close, message)


@command(
    synopsis=("$ gas commit tb:<dataset_name>#<draft_number> [-m <title>]      # Commit a draft.",)
)
@click.argument("tbrn", type=str)
@click.option(
    "-m", "--message", type=str, multiple=True, default=(), help="The title of the commit."
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
        "# Show commit logs.",
        "$ gas log tb:<dataset_name>[@<revision>]",
        "",
        "# Show up to <number> commit logs.",
        "$ gas log -n <number> tb:<dataset_name>[@<revision>]",
        "",
        "# Show oneline commit logs.",
        "$ gas log --oneline tb:<dataset_name>[@<revision>]",
        "",
        "# Show all commit logs.",
        "$ gas log --all tb:<dataset_name>",
        "",
        "# Show text-based graphical commit logs.",
        "$ gas log --graph tb:<dataset_name>[@<revision>]",
    )
)
@click.argument("tbrn", type=str)
@click.option(
    "-n", "--max-count", type=int, default=None, help="Limit the max number of commits to show"
)
@click.option("--oneline", is_flag=True, help="Limit commit message to oneline")
@click.option("--all", "is_all", is_flag=True, help="Show all the commits of all branches")
@click.option("--graph", is_flag=True, help="Show text-based graphical commits history")
@click.pass_obj
def log(  # pylint: disable=too-many-arguments
    obj: Dict[str, str],
    tbrn: str,
    max_count: Optional[int],
    oneline: bool,
    is_all: bool,
    graph: bool,
) -> None:
    """Show commit logs.\f

    Arguments:
        obj: A dict contains config information.
        tbrn: The tbrn of a dataset.
        max_count: Max number of commits to show.
        oneline: Whether to show a commit message in oneline.
        is_all: Whether to show all commits of all branches.
        graph: Whether to show graphical commit history.

    """  # noqa: D301,D415
    from .log import _implement_log

    _implement_log(obj, tbrn, max_count, oneline, is_all, graph)


@command(
    synopsis=(
        "$ gas auth                      # Interactive authentication.",
        "$ gas auth <AccessKey>          # Authenticate with AccessKey.",
        "$ gas auth -g [-a]              # Get the authentication info.",
        "$ gas auth -s [-a]              # Get the authentication and user info.",
        "$ gas auth -u [-a]              # Unset the authentication info.",
    )
)
@click.argument("arg1", type=str, default="", metavar="accessKey")
@click.argument("arg2", type=str, default="", metavar="")
@click.option("-g", "--get", is_flag=True, help="Get the accesskey of the profile")
@click.option(
    "-s", "--status", is_flag=True, help="Get the user info and accesskey of the profile."
)
@click.option("-u", "--unset", is_flag=True, help="Unset the accesskey of the profile")
@click.option("-a", "--all", "is_all", is_flag=True, help="All the auth info")
@click.pass_obj
def auth(  # pylint: disable=too-many-arguments
    obj: Dict[str, str], arg1: str, arg2: str, get: bool, status: bool, unset: bool, is_all: bool
) -> None:
    """Authenticate the accessKey of gas.\f

    Arguments:
        obj: A dict contains config information.
        arg1: The accessKey or the url of gas for the authentication.
        arg2: The accessKey of gas for the authentication if arg1 is url.
        get: Whether to get the accesskey of the profile.
        status: Whether to get the user info and accesskey of the profile.
        unset: Whether to unset the accesskey of the profile.
        is_all: All the auth info or not.

    """  # noqa: D301,D415
    from .auth import _implement_auth

    _implement_auth(obj, arg1, arg2, get, status, unset, is_all)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
