# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import os
import shutil
import sys
import tomllib
from pathlib import Path

# Make the package importable without installation (local builds);
# on Read the Docs the package is also pip-installed (see .readthedocs.yaml).
DOCS_SOURCE = Path(__file__).resolve().parent
REPO_ROOT = DOCS_SOURCE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

on_rtd = os.environ.get('READTHEDOCS') == 'True'

with open(REPO_ROOT / 'pyproject.toml', 'rb') as f:
    _pyproject = tomllib.load(f)['project']

# Tutorials are the notebooks of the repository's notebook/ folder, copied
# here at each build so that the docs never diverge from them. A title cell is
# prepended to the copy when the notebook does not start with one.
TUTORIALS = {
    'basic_visualization.ipynb': None,
    'optimal_geometries.ipynb': 'Optimal viewing geometries',
}
for _nb, _title in TUTORIALS.items():
    with open(REPO_ROOT / 'notebook' / _nb) as f:
        _content = json.load(f)
    if _title is not None:
        _content['cells'].insert(0, {'cell_type': 'markdown', 'metadata': {},
                                     'source': [f'# {_title}']})
    with open(DOCS_SOURCE / 'tutorials' / _nb, 'w') as f:
        json.dump(_content, f)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'surface_sky_radiance_ratio'
copyright = '2023, Tristan Harmel'
author = 'Tristan Harmel'
release = _pyproject['version']
version = '.'.join(release.split('.')[:2])
today_fmt = '%Y-%m-%d'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'myst_nb',
    'IPython.sphinxext.ipython_console_highlighting',
]

templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '_readme.md', '**.ipynb_checkpoints', 'Thumbs.db', '.DS_Store']

# the README (included in index.rst) starts at heading level 3 once its title
# line is skipped
suppress_warnings = ['myst.header']

# -- Autodoc / autosummary ---------------------------------------------------

autosummary_generate = True
autoclass_content = 'class'
autodoc_typehints = 'description'
# 'members' is set in the autosummary templates (_templates/) to avoid
# documenting objects twice
autodoc_default_options = {
    'member-order': 'bysource',
    'show-inheritance': True,
}

# NumPy-style docstrings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False

todo_include_todos = True

# -- Math --------------------------------------------------------------------

# number labelled equations and refer to them as "Eq. (n)" with :eq:
math_eqref_format = 'Eq. ({number})'
math_numfig = True
numfig = True

# LaTeX macros shared by the .rst pages (MathJax) and notebooks/Markdown (MyST)
mathjax3_config = {
    'tex': {
        'macros': {
            'Rrs': r'R_{\mathrm{rs}}',
            'Rss': r'R_{\mathrm{ss}}',
        },
    },
}
# same macros for the PDF build (Read the Docs builds all formats)
latex_elements = {
    'preamble': r'\newcommand{\Rrs}{R_{\mathrm{rs}}}'
                r'\newcommand{\Rss}{R_{\mathrm{ss}}}',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'pandas': ('https://pandas.pydata.org/docs', None),
    'xarray': ('https://docs.xarray.dev/en/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_book_theme'
pygments_style = 'sphinx'

html_theme_options = {
    'repository_url': 'https://github.com/Tristanovsk/surface_sky_radiance_ratio',
    'repository_branch': 'main',
    'path_to_docs': 'docs/source',
    'use_repository_button': True,
    'use_issues_button': True,
    'use_edit_page_button': True,
    'use_download_button': True,
    'navigation_with_keys': True,
    'show_toc_level': 2,
    'secondary_sidebar_items': ['page-toc', 'edit-this-page'],
}

html_title = 'surface_sky_radiance_ratio'

html_static_path = ['_static']
html_show_sourcelink = False
html_last_updated_fmt = today_fmt

htmlhelp_basename = 'surface_sky_radiance_ratio_doc'

# -- MyST / notebook rendering -----------------------------------------------

myst_enable_extensions = [
    'amsmath',
    'colon_fence',
    'deflist',
    'dollarmath',
    'html_admonition',
    'html_image',
    'linkify',
    'replacements',
    'smartquotes',
    'substitution',
]

# Notebooks rely on the full look-up table and external data (GLORIA) that are
# not available on Read the Docs: they are rendered with their saved outputs.
nb_execution_mode = 'off'
nb_merge_streams = True


# -- README illustrations ----------------------------------------------------

# The README uses HTML <img> tags (to center images on GitHub), whose paths are
# not rewritten by MyST: copy the illustration folder next to the HTML pages.
def _copy_illustrations(app, exception):
    if exception is None and app.builder.format == 'html':
        shutil.copytree(REPO_ROOT / 'illustration',
                        Path(app.outdir) / 'illustration', dirs_exist_ok=True)


def setup(app):
    app.connect('build-finished', _copy_illustrations)
