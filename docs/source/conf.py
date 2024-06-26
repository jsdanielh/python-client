# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import warnings
import os
import sys

# Source code dir relative to this file
sys.path.insert(0, os.path.abspath("../.."))
# Temp. workaround for https://github.com/agronholm/sphinx-autodoc-typehints/issues/133

warnings.filterwarnings(
    "ignore", message="sphinx.util.inspect.Signature\(\) is deprecated"
)

# -- Project information -----------------------------------------------------

project = "Albatross Nimiq Python Client"
author = "jsdanielh"

# The full version, including alpha/beta/rc tags
release = "1.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # Core Sphinx library for auto html doc generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables for modules/classes/methods etc
    # Add a link to the Python source code for classes, functions etc.
    "sphinx.ext.viewcode",
    # Automatically document param types (less noise in class signature)
    "sphinx_autodoc_typehints",
    "m2r2",  # m2r2 converts a markdown file to a valid rst format.
]

# source_suffix = '.rst'
source_suffix = [".rst", ".md"]

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = (
    False  # Remove 'view source code' from top of page (for html, not python)
)
# If no class summary, inherit base class summary
autodoc_inherit_docstrings = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# -- Options for HTML output -------------------------------------------------

# on_rtd is whether on readthedocs.org, this line of code grabbed from docs.readthedocs.org...
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_copy_source = False
