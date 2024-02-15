# ruff: noqa

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("src"))


# -----------------------------------------------------------------------------
# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# -----------------------------------------------------------------------------

author = "Kennedy Kori"
copyright = "2024, Kennedy Kori"
project = "credrails-reconciler"


# -----------------------------------------------------------------------------
# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# -----------------------------------------------------------------------------

extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary"]

# Preserve authored syntax for defaults
autodoc_preserve_defaults = True

autodoc_default_flags = {
    "inherited-members": True,
    "show-inheritance": True,
    "special-members": (
        "__enter__",
        "__exit__",
        "__call__",
        "__getattr__",
        "__setattr_",
    ),
}

autodoc_member_order = "groupwise"

autoapi_python_use_implicit_namespaces = True

autosummary_generate = True  # Turn on sphinx.ext.autosummary

exclude_patterns = []

# Be strict about any broken references
nitpicky = True

nitpick_ignore = []

templates_path = ["_templates"]

root_doc = "index"


# -----------------------------------------------------------------------------
# Options for HTML output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# -----------------------------------------------------------------------------

html_logo = "images/reconciler-logo.svg"

html_static_path = ["_static"]

html_theme = "furo"

html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": "#4f54f8",
        "color-brand-content": "#4f54f8",
    },
    "dark_css_variables": {
        "color-brand-primary": "#4f54f8",
        "color-brand-content": "#4f54f8",
    },
}


# -----------------------------------------------------------------------------
# Include Python intersphinx mapping to prevent failures
# jaraco/skeleton#51
# -----------------------------------------------------------------------------

extensions += ["sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "peps": ("https://peps.python.org/", None),
    "python": ("https://docs.python.org/3", None),
    "pypackage": ("https://packaging.python.org/en/latest/", None),
    "importlib-resources": (
        "https://importlib-resources.readthedocs.io/en/latest",
        None,
    ),
    "django": (
        "http://docs.djangoproject.com/en/dev/",
        "http://docs.djangoproject.com/en/dev/_objects/",
    ),
}


# -----------------------------------------------------------------------------
# Support tooltips on references
# -----------------------------------------------------------------------------

extensions += ["hoverxref.extension"]
hoverxref_auto_ref = True
hoverxref_intersphinx = [
    "python",
    "pip",
    "pypackage",
    "importlib-resources",
    "django",
]


# -----------------------------------------------------------------------------
# Add support for nice Not Found 404 pages
# -----------------------------------------------------------------------------

extensions += ["notfound.extension"]


# -----------------------------------------------------------------------------
# Add icons (aka "favicons") to documentation
# -----------------------------------------------------------------------------

extensions += ["sphinx_favicon"]
html_static_path += ["images"]  # should contain the folder with icons

# List of dicts with <link> HTML attributes
# static-file points to files in the html_static_path (href is computed)

favicons = [
    {
        "rel": "icon",
        "type": "image/svg+xml",
        "static-file": "reconciler-logo.svg",
        "sizes": "any",
    },
]
