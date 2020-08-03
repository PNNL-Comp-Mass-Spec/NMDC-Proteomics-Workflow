# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, basedir)

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    html_theme = 'default'


def setup(app):
    app.add_css_file('custom.css')

# -- Project information -----------------------------------------------------

project = 'Meta-Proteomics Workflow'
copyright = '2020, Anubhav'
author = 'Anubhav'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- Options for Napoleon Extension --------------------------------------------

# Parse Google style docstrings.
# See http://google.github.io/styleguide/pyguide.html
napoleon_google_docstring = True

# Parse NumPy style docstrings.
# See https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
napoleon_numpy_docstring = True

# Should special members (like __membername__) and private members
# (like _membername) members be included in the documentation if they
# have docstrings.
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# If True, docstring sections will use the ".. admonition::" directive.
# If False, docstring sections will use the ".. rubric::" directive.
# One may look better than the other depending on what HTML theme is used.
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False

# If True, use Sphinx :ivar: directive for instance variables:
#     :ivar attr1: Description of attr1.
#     :type attr1: type
# If False, use Sphinx .. attribute:: directive for instance variables:
#     .. attribute:: attr1
#
#        Description of attr1.
#
#        :type: type
napoleon_use_ivar = False

# If True, use Sphinx :param: directive for function parameters:
#     :param arg1: Description of arg1.
#     :type arg1: type
# If False, output function parameters using the :parameters: field:
#     :parameters: **arg1** (*type*) -- Description of arg1.
napoleon_use_param = True

# If True, use Sphinx :rtype: directive for the return type:
#     :returns: Description of return value.
#     :rtype: type
# If False, output the return type inline with the return description:
#     :returns: *type* -- Description of return value.
napoleon_use_rtype = True

# -- Autodoc configuration -----------------------------------------------------

autoclass_content = 'class'

autodoc_member_order = 'bysource'

autodoc_default_flags = ['members']

# -- General configuration -----------------------------------------------------

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
              'sphinx.ext.doctest',
              'sphinx.ext.coverage',
              'sphinx.ext.viewcode',
              'sphinx.ext.intersphinx',
              'sphinxcontrib.napoleon',
              'sphinxarg.ext',
              'sphinxcontrib.images',
]

intersphinx_mapping = {
  'pockets': ('https://pockets.readthedocs.io/en/latest/', None),
  'python': ('https://docs.python.org/3', None),
  'sphinx': ('http://sphinx.readthedocs.io/en/latest/', None)
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_logo = "mepro_headshot.png"
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
 }

# html_theme_path = ["../.."]

html_show_sourcelink = True
    # "pydata_sphinx_theme"
# "pallets-sphinx-themes"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_context = {
    'css_files': [
        '_static/theme_overrides.css',  # override wide tables in RTD theme
        ],
     }