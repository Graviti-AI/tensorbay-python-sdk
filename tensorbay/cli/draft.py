#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Implementation of gas draft."""

import sys
from typing import Dict

import click

from .tbrn import TBRN, TBRNType


def _implement_draft(
    obj: Dict[str, str], tbrn: str, is_list: bool, title: str  # pylint: disable=unused-argument
) -> None:
    info = TBRN(tbrn=tbrn)

    if info.type != TBRNType.DATASET:
        click.echo(f'To operate a draft, "{info}" must be a dataset', err=True)
        sys.exit(1)

    if is_list:
        pass

    elif title:
        pass

    else:
        pass
