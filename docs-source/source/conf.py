# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'QuartzBio'
copyright = '2025 Precision for Medicine, inc.'
author = 'QuartzBio'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_mdinclude',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_theme_options = {
    "extra_nav_links": {
        "Current Version: v1.2.0": "https://pypi.org/project/quartzbio/",
    }
}
html_static_path = ['_static']

import os
import sys
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'quartzbio'))
sys.path.insert(0, basedir)
