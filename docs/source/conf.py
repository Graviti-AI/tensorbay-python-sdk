#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=missing-module-docstring,invalid-name
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
"""Configuration file for the Sphinx documentation builder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))


# -- Project information -----------------------------------------------------

project = "TensorBay"
copyright = "2021, Graviti"  # pylint: disable=redefined-builtin
author = "Graviti"

# The full version, including alpha/beta/rc tags
# release = "0.3.10"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # used for generating doc automatically
    "sphinx.ext.viewcode",  # used for imbedding source code automatically
    "sphinx.ext.autosummary",  # used for creating summary table automatically
    "sphinx.ext.todo",  # used for recording todo and todolist
    "sphinx.ext.ifconfig",  # used for configuration based on different condtitions
    "sphinx.ext.intersphinx",  # used for embedding doc links from other project such as python
    "sphinx.ext.autosectionlabel",  # used for referring sections in a rst file
    "sphinx.ext.napoleon",  # used for being compatible with Google and Numpy doc style
    "sphinx.ext.coverage",  # used for generating doc coverage report
]

# extensions_config
autosummary_generate = True
todo_include_todos = True
autosectionlabel_prefix_document = True
numfig = True

# The default options for autodoc
autodoc_default_options = {"member-order": "bysource"}
autodoc_typehints = "description"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_favicon = "images/favicon.svg"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
