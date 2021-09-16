#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

# pylint: disable=wrong-import-position
# pylint: disable=not-callable
# pylint: disable=import-error
# pylint: disable=pointless-string-statement

"""This file includes the python code of profile."""


"""Usage of Profile"""
from tensorbay.client import profile

# Start record.
with profile as pf:
    # <Your Program>

    # Save the statistical record to a file.
    pf.save("summary.txt", file_type="txt")
""""""

"""Usage of Multiprocess"""
# Start record.
profile.start(multiprocess=True)

# <Your Program>

# Save the statistical record to a file.
profile.save("summary.txt", file_type="txt")
profile.stop()
""""""
