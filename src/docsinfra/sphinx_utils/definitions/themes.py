"""
Possible Sphinx themes.
"""
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass
class _SphinxTheme:
    """
    Represents a possible Sphinx theme.
    """

    name: str
    description: str
    example_url: str


# TODO: sphinx_book_theme fails because of the genindex in table_of_contents.rst
_THEMES = [
    _SphinxTheme(
        name="insipid",
        description="clean and minimal, light mode only",
        example_url="https://sphinx-themes.org/sample-sites/insipid-sphinx-theme/",
    ),
    _SphinxTheme(
        name="furo",
        description="clean customisable theme, light and dark modes",
        example_url="https://pradyunsg.me/furo/",
    ),
    _SphinxTheme(
        name="piccolo_theme",
        description="minimal, light and dark modes",
        example_url="https://sphinx-themes.org/sample-sites/piccolo-theme/",
    ),
    _SphinxTheme(
        name="sphinx_rtd_theme",
        description="Read The Docs theme, light mode only",
        example_url="https://sphinx-themes.org/sample-sites/sphinx-rtd-theme/",
    ),
    _SphinxTheme(
        name="classic",
        description="builtin, light mode only",
        example_url="https://sphinx-themes.org/sample-sites/default-classic/",
    ),
    _SphinxTheme(
        name="sphinxdoc",
        description="builtin, light mode only",
        example_url="https://sphinx-themes.org/sample-sites/default-sphinxdoc/",
    ),
]


class ConfigurableThemes(Mapping[str, _SphinxTheme]):
    def __init__(self):
        self._themes = {theme.name: theme for theme in _THEMES}

    def __len__(self) -> int:
        return len(self._themes)

    def __iter__(self):
        return iter(self._themes)

    def __getitem__(self, key: str) -> _SphinxTheme:
        return self._themes[key]

    @property
    def default(self) -> _SphinxTheme:
        return self["furo"]  # Using furo in release branch


THEMES = ConfigurableThemes()
