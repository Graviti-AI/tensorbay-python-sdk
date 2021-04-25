#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Command-line interface.

Use 'gas' + COMMAND in terminal to operate on datasets.

Use 'gas config' to  configure environment.

Use 'gas create' to create a dataset.

Use 'gas delete' to delete a dataset.

Use 'gas ls' to list data.

Use 'gas cp' to upload data.

Use 'gas rm' to delete data.

"""

import logging
import os
import sys
from configparser import ConfigParser
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, Iterator, Tuple, Union

import click

from ..__verison__ import __version__
from ..dataset import Data, Segment
from ..utility import TBRN, TBRNType
from .gas import GAS
from .requests import config as client_config
from .segment import FusionSegmentClient, SegmentClient


def _config_filepath() -> str:
    """Get the path of the config file.

    Returns:
        The path of the config file.

    """
    home = "USERPROFILE" if os.name == "nt" else "HOME"
    return os.path.join(os.environ[home], ".gasconfig")


def _read_config(config_filepath: str, profile_name: str) -> Tuple[str, str]:
    """Read accessKey and URL from the config file.

    Arguments:
        config_filepath: The file containing config info.
        profile_name: The environment to login.

    Returns:
        The accessKey of profile_name read from the config file.
        The URL of profile_name read from the config file.

    """
    if not os.path.exists(config_filepath):
        click.echo(
            f"{config_filepath} not exist"
            "\n\nPlease use 'gas config <accessKey>' to create config file",
            err=True,
        )
        sys.exit(1)

    config_parser = ConfigParser()
    config_parser.read(config_filepath)
    access_key = config_parser[profile_name]["accessKey"]
    url = config_parser[profile_name]["url"] if "url" in config_parser[profile_name] else ""
    return access_key, url


def _gas(access_key: str, url: str, profile_name: str) -> GAS:
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
        access_key, url = _read_config(_config_filepath(), profile_name)

    if not access_key:
        click.echo("accessKey should be appointed", err=True)
        sys.exit(1)

    return GAS(access_key, url)


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
    ctx.obj = {
        "access_key": access_key,
        "url": url,
        "profile_name": profile_name,
    }
    client_config._x_source = "PYTHON-CLI"  # pylint: disable=protected-access

    if debug:
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.argument("name", type=str)
@click.pass_obj
def create(obj: Dict[str, str], name: str) -> None:
    """Create a dataset.\f

    Arguments:
        obj: A dict including config information.
        name: The name of the dataset to be created, like "tb:KITTI".

    """  # noqa: D301,D415
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)
    _gas(**obj).create_dataset(info.dataset_name)


# @cli.command()
# @click.argument("name", type=str)
# @click.argument("message", type=str)
# @click.argument("tag", type=str, required=False)
# @click.pass_obj
# def commit(obj: Dict[str, str], name: str, message: str, tag: str) -> None:
#     """Commit a dataset.\f

#     Arguments:
#         obj: A dict including config information.
#         name: The name of the dataset to be committed, like "tb:KITTI".
#         message: The message of the dataset to be committed.
#         tag: The tag of the dataset to be committed.

#     """
#     info = TBRN(tbrn=name)
#     if info.type != TBRNType.DATASET:
#         click.echo(f'"{name}" is not a dataset', err=True)
#         sys.exit(1)
#     dataset = _gas(**obj)._get_dataset(info.dataset_name)  # pylint: disable=protected-access
#     dataset.commit(message, tag=tag)


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
    info = TBRN(tbrn=name)
    if info.type != TBRNType.DATASET:
        click.echo(f'"{name}" is not a dataset', err=True)
        sys.exit(1)

    if not yes:
        click.confirm(
            f'Dataset "{name}" will be completely deleted.\nDo you want to continue?', abort=True
        )

    _gas(**obj).delete_dataset(info.dataset_name)


def _get_segment_object(
    segment_name: str,
    local_abspaths: Iterable[str],
    remote_path: str,
    is_recursive: bool,
) -> Segment:
    """Get the pair of local_path and remote_path.

    Arguments:
        segment_name: The name of the segment these data belong to.
        local_abspaths: A list of local abstract paths, could be folder or file.
        remote_path: The remote object path, not necessarily end with '/'.
        is_recursive: Whether copy directories recursively.

    Returns:
        A segment contains mapping data.

    """
    segment = Segment(segment_name)
    for local_abspath in local_abspaths:
        if not os.path.isdir(local_abspath):
            data = Data(
                local_abspath,
                target_remote_path=str(PurePosixPath(remote_path, os.path.basename(local_abspath))),
            )
            segment.append(data)
            continue

        if not is_recursive:
            click.echo(
                "Error: local paths include directories, please use -r option",
                err=True,
            )
            sys.exit(1)

        local_abspath = os.path.normpath(local_abspath)
        folder_name = os.path.basename(local_abspath)
        for root, _, filenames in os.walk(local_abspath):
            relpath = os.path.relpath(root, local_abspath) if root != local_abspath else ""
            for filename in filenames:
                data = Data(
                    os.path.join(root, filename),
                    target_remote_path=str(
                        PurePosixPath(Path(remote_path, folder_name, relpath, filename))
                    ),
                )
                segment.append(data)
    return segment


def _echo_segment(
    dataset_name: str,
    segment_name: str,
    segment: Union[SegmentClient, FusionSegmentClient],
    list_all_files: bool,
) -> None:
    """Echo a segment.

    Arguments:
        dataset_name: The name of the dataset.
        segment_name: The name of the segment.
        segment: A segment or a fusion segment.
        list_all_files: Only works when segment is a fusion one.
            If False, list frame indexes only.
            If True, list sensors and files, too.

    """
    if isinstance(segment, SegmentClient):
        _echo_data(dataset_name, segment_name, segment.list_data_paths())
    else:
        frames = segment.list_frames()
        if not list_all_files:
            for index, _ in enumerate(frames):
                click.echo(TBRN(dataset_name, segment_name, index).get_tbrn())
        else:
            for index, frame in enumerate(frames):
                for sensor_name, data in frame.items():
                    click.echo(
                        TBRN(
                            dataset_name,
                            segment_name,
                            index,
                            sensor_name,
                            remote_path=data.path,
                        )
                    )


def _echo_data(dataset_name: str, segment_name: str, data_iter: Iterable[str]) -> None:
    """Echo files in data_iter under 'tb:dataset_name:segment_name'.

    Arguments:
        dataset_name: The name of the dataset the segment belongs to.
        segment_name: The name of the segment.
        data_iter: Iterable data to be echoed.

    """
    for data in data_iter:
        click.echo(TBRN(dataset_name, segment_name, remote_path=data).get_tbrn())


def _ls_dataset(gas: GAS, info: TBRN, list_all_files: bool) -> None:
    dataset = gas._get_dataset_with_any_type(info.dataset_name)  # pylint: disable=protected-access
    segment_names = dataset.list_segment_names()
    if not list_all_files:
        for segment_name in segment_names:
            click.echo(TBRN(info.dataset_name, segment_name).get_tbrn())
        return

    for segment_name in segment_names:
        segment = dataset.get_segment(segment_name)
        _echo_segment(info.dataset_name, segment_name, segment, list_all_files)


def _ls_segment(gas: GAS, info: TBRN, list_all_files: bool) -> None:
    dataset = gas._get_dataset_with_any_type(info.dataset_name)  # pylint: disable=protected-access
    _echo_segment(
        info.dataset_name, info.segment_name, dataset.get_segment(info.segment_name), list_all_files
    )


def _ls_frame(gas: GAS, info: TBRN, list_all_files: bool) -> None:
    dataset_client = gas.get_dataset(info.dataset_name, is_fusion=True)
    segment_client = dataset_client.get_segment(info.segment_name)

    try:
        frame = segment_client.list_frames()[info.frame_index]
    except IndexError:
        click.echo(f'No such frame: "{info.frame_index}"!', err=True)
        sys.exit(1)

    if not list_all_files:
        for sensor_name in frame:
            click.echo(TBRN(info.dataset_name, info.segment_name, info.frame_index, sensor_name))
    else:
        for sensor_name, data in frame.items():
            click.echo(
                TBRN(
                    info.dataset_name,
                    info.segment_name,
                    info.frame_index,
                    sensor_name,
                    remote_path=data.path,
                )
            )


def _ls_sensor(
    gas: GAS,
    info: TBRN,
    list_all_files: bool,  # pylint: disable=unused-argument
) -> None:
    dataset_client = gas.get_dataset(info.dataset_name, is_fusion=True)
    segment_client = dataset_client.get_segment(info.segment_name)
    try:
        frame = segment_client.list_frames()[info.frame_index]
    except IndexError:
        click.echo(f'No such frame: "{info.frame_index}"!', err=True)
        sys.exit(1)

    data = frame[info.sensor_name]
    click.echo(
        TBRN(
            info.dataset_name,
            info.segment_name,
            info.frame_index,
            info.sensor_name,
            remote_path=data.path,
        )
    )


def _ls_fusion_file(
    gas: GAS,
    info: TBRN,
    list_all_files: bool,  # pylint: disable=unused-argument
) -> None:
    dataset_client = gas.get_dataset(info.dataset_name, is_fusion=True)
    segment_client = dataset_client.get_segment(info.segment_name)
    try:
        frame = segment_client.list_frames()[info.frame_index]
    except IndexError:
        click.echo(f'No such frame: "{info.frame_index}"!', err=True)
        sys.exit(1)

    if frame[info.sensor_name].path != info.remote_path:
        click.echo(f'No such file: "{info.remote_path}"!', err=True)
        sys.exit(1)

    click.echo(info)


def _ls_normal_file(  # pylint: disable=unused-argument
    gas: GAS, info: TBRN, list_all_files: bool
) -> None:
    dataset_client = gas.get_dataset(info.dataset_name)
    segment_client = dataset_client.get_segment(info.segment_name)
    _echo_data(
        info.dataset_name,
        info.segment_name,
        _filter_data(segment_client.list_data_paths(), info.remote_path),
    )


_LS_FUNCS = {
    TBRNType.DATASET: _ls_dataset,
    TBRNType.SEGMENT: _ls_segment,
    TBRNType.NORMAL_FILE: _ls_normal_file,
    TBRNType.FRAME: _ls_frame,
    TBRNType.FRAME_SENSOR: _ls_sensor,
    TBRNType.FUSION_FILE: _ls_fusion_file,
}


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
    gas = _gas(**obj)

    if not tbrn:
        for dataset_name in gas.list_dataset_names():
            click.echo(TBRN(dataset_name).get_tbrn())
        return

    info = TBRN(tbrn=tbrn)
    _LS_FUNCS[info.type](gas, info, list_all_files)


def _filter_data(
    data_list: Iterable[str], remote_path: str, is_recursive: bool = True
) -> Iterator[str]:
    """Get a list of paths under the remote_path.

    Arguments:
        data_list: A list of candidate paths.
        remote_path: The remote path to filter data.
        is_recursive: Whether to filter data recursively.

    Returns:
        A list of paths under the given remote_path.

    """
    if is_recursive:
        return (
            filter(lambda x: x.startswith(remote_path), data_list)
            if remote_path.endswith("/")
            else filter(lambda x: x.startswith(remote_path + "/") or x == remote_path, data_list)
        )
    return filter(lambda x: x == remote_path, data_list)


#
# @cli.command()
# @click.argument("tbrn", type=str)
# @click.option(
#     "-r", "--recursive", "is_recursive", is_flag=True, help="Remove directories recursively."
# )
# @click.option("-f", "--force", "force_delete", is_flag=True, help="Force to delete any segment.")
# @click.pass_obj
# # pylint: disable=invalid-name
# def rm(obj: Dict[str, str], tbrn: str, is_recursive: bool, force_delete: bool) -> None:
#     """Remove the remote paths.\f
#
#     :param obj: a dict including config info
#     :param tbrn: path to be removed, like "tb:KITTI:seg1".
#     :param is_recursive: whether remove directories recursively
#     :param force_delete: sensor and its objects will also be deleted if True,
#       else only segment with no sensor can be deleted.
#     """
#     gas = _gas(**obj)
#     info = TBRN(tbrn=tbrn)
#     dataset = gas.get_dataset(info.dataset_name)
#
#     if info.type == TBRNType.DATASET:
#         if not is_recursive:
#             click.echo("Error: please use -r option to remove the whole dataset", err=True)
#             sys.exit(1)
#         segment_names = dataset.list_segment_names()
#         dataset.delete_segments(segment_names, force_delete)
#         return
#
#     if info.type == TBRNType.SEGMENT:
#         if not is_recursive:
#             click.echo("Error: please use -r option to remove the whole segment", err=True)
#             sys.exit(1)
#         dataset.delete_segments(info.segment_name, force_delete)
#         return
#
#     if info.type == TBRNType.NORMAL_FILE:
#         if not is_recursive and info.remote_path.endswith("/"):
#             click.echo("Error: please use -r option to remove recursively", err=True)
#             sys.exit(1)
#
#         segment = dataset.get_segment(info.segment_name)
#         filter_data = list(_filter_data(segment.list_data(), info.remote_path, is_recursive))
#         if not filter_data:
#             echo_info = "file or directory" if is_recursive else "file"
#             click.echo(f'Error: no such {echo_info} "{tbrn}" ', err=True)
#             sys.exit(1)
#         segment.delete_data(filter_data)
#         return
#
#     click.echo(f'"{tbrn}" is an invalid path to remove', err=True)
#     sys.exit(1)


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
    config_file = _config_filepath()
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


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
