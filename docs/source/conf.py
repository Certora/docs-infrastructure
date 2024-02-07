# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import docsinfra
from docsinfra.sphinx_utils import TAGS, CVL2Lexer

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Certora Documents Infrastructure"
copyright = "2024, Certora, Inc"
author = "Certora, Inc"
release = docsinfra.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Ensure this is always a dev-build
# See https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#tags
tags.add(TAGS.is_dev_build)  # noqa: F821

extensions = [
    "docsinfra.sphinx_utils.codelink_extension",
    "docsinfra.sphinx_utils.includecvl",
    "sphinx.ext.graphviz",
    "sphinx.ext.todo",
    "sphinxcontrib.video",  # See https://sphinxcontrib-video.readthedocs.io/en/latest/
    "sphinxcontrib.youtube",  # See https://sphinxcontrib-youtube.readthedocs.io
    "sphinx_design",
    "sphinxarg.ext",  # See https://sphinx-argparse.readthedocs.io/en/latest/index.html
    "sphinxcontrib.spelling",  # See https://sphinxcontrib-spelling.readthedocs.io/
    "sphinxarg.ext",  # See https://sphinx-argparse.readthedocs.io/en/latest/index.html
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = [
    "**/glossary_example.rst",  # Prevent warning on duplicate term description
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_short_title = "Certora Docs Infra"

# The html_title also appears in the side-bar, different title to indicate dev-build.
html_title = (
    f"{project} - Development" if tags.has(TAGS.is_dev_build) else project  # noqa: F821
)


# -- themes customizations -----------------------------------------------------
html_theme_options = {
    "light_logo": "logo.svg",
    "dark_logo": "logo.svg",
}
# NOTE: For other themes use the following line:
# html_logo = "_static/logo.svg"


# -- prologue ----------------------------------------------------------------
# A string of reStructuredText that will be included at the beginning of every source
# file that is read.
# Use the prologue to add inline cvl code and solidity code.
rst_prolog = """
.. role:: cvl(code)
   :language: cvl

.. role:: solidity(code)
   :language: solidity
"""


# -- autodoc -----------------------------------------------------------------
add_module_names = False


# -- codelink_extension configuration ----------------------------------------
code_path_override = "../../code/"
link_to_github = True


# -- todo extension configuration --------------------------------------------
# Do not show todo list unless in dev build
todo_include_todos = tags.has(TAGS.is_dev_build)  # noqa: F821


# -- spelling configuration --------------------------------------------------
# See https://sphinxcontrib-spelling.readthedocs.io/en/latest/customize.html
spelling_lang = "en_US"
spelling_word_list_filename = [
    "spelling_wordlist.txt",
    "packages_spelling_wordlist.txt",
]


# -- add CVL syntax highlighting ---------------------------------------------
def setup(sphinx):
    sphinx.add_lexer("cvl", CVL2Lexer)
