"""
A script for starting a Certora document project.
"""
from argparse import ArgumentParser, Namespace
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from typing import Any

from sphinx.cmd.quickstart import DEFAULTS, generate

from ..sphinx_utils.definitions.themes import THEMES


def get_quickstart_parser() -> ArgumentParser:
    """
    Returns the :class:`argparse.ArgumentParser` for :class:`.Quickstart`.
    """
    parser = ArgumentParser(
        description="Quickly start a Certora document project",
    )

    parser.add_argument(
        "path",
        metavar="PROJECT_DIR",
        type=Path,
        default=Path.cwd(),
        nargs="?",
        help="project root path, defaults to current working dir",
    )
    parser.add_argument(
        "-p",
        "--project",
        metavar="PROJECT",
        dest="project",
        required=True,
        help="project name",
    )

    versioning = parser.add_argument_group(
        "Versioning",
        'Sphinx supports a notion of a "version" and a "release" for the project.',
    )
    versioning.add_argument(
        "-v",
        "--version",
        metavar="VERSION",
        dest="version",
        default="",
        help="version of project",
    )
    versioning.add_argument(
        "-r", "--release", metavar="RELEASE", dest="release", help="release of project"
    )

    styling = parser.add_argument_group(
        "Style",
        "Available themes: "
        + "; ".join(f"{theme.name} - {theme.description}" for theme in THEMES.values()),
    )
    styling.add_argument(
        "--theme",
        metavar="HTML_THEME",
        dest="html_theme",
        choices=[name for name in THEMES],
        default=THEMES.default.name,
        help=f"html theme for the project, defaults to {THEMES.default.name}",
    )

    codeing = parser.add_argument_group(
        "Code links", "Determine location to search for code and link style."
    )
    codeing.add_argument(
        "--code",
        metavar="CODE_PATH",
        dest="code_path",
        default="",
        help="path of code folder, relative to the source dir, defaults to source dir",
    )
    codeing.add_argument(
        "--no-link-to-github",
        dest="link_to_github",
        action="store_false",
        help="link to local files instead of github",
    )
    return parser


def _default_extensions():
    return [
        "sphinx.ext.graphviz",
        "sphinx.ext.todo",
        "sphinxcontrib.video",  # See https://sphinxcontrib-video.readthedocs.io/en/latest/
        "sphinxcontrib.youtube",  # See https://sphinxcontrib-youtube.readthedocs.io
        "sphinx_design",
        "sphinxarg.ext",  # See https://sphinx-argparse.readthedocs.io/en/latest/index.html
        "sphinxcontrib.spelling",  # See https://sphinxcontrib-spelling.readthedocs.io/
    ]


@dataclass
class QuickstartConfig:
    path: Path
    project: str  # Project name
    copyright: str = field(init=False)  # Copyright - determined in __post_init__
    html_theme: str = THEMES.default

    # Path to code folder, see
    # https://www.sphinx-doc.org/en/master/extdev/envapi.html#sphinx.environment.BuildEnvironment.relfn2path
    code_path: str = ""  # Path to code folder
    link_to_github: bool = True  # Link to Github vs linking locally

    # Modifiable values
    version: str = ""  # Version of project
    release: str = ""  # Release of project

    # Fixed values
    author: str = "Certora, Inc"  # Author name
    language: str = "en"  # Document language
    sep: bool = True  # separate source and build dirs
    dot: str = DEFAULTS["dot"]  # replacement for dot in _templates folder etc.
    master: str = DEFAULTS["master"]  # master document name ("index")
    suffix: str = DEFAULTS["suffix"]  # source file suffix (".rst")
    makefile: bool = False  # Generate a Makefile
    batchfile: bool = False  # Generate a command file
    extensions: list[str] = field(default_factory=_default_extensions)
    spelling_word_list_filename: str = (
        "spelling_wordlist.txt"  # For sphinxcontrib.spelling
    )

    def __post_init__(self):
        today = datetime.today()
        self.copyright = f"{today.year}, {self.author}"

        # Ensure the code path is given as absolute, since these are relative to the
        # source dir. See:
        # https://www.sphinx-doc.org/en/master/extdev/envapi.html#sphinx.environment.BuildEnvironment.relfn2path
        code = Path(self.code_path)
        if not code.is_absolute():
            self.code_path = "/" + self.code_path  # TODO: use `os.sep` instead of "/"

    @classmethod
    def from_args(cls, args: Namespace) -> "QuickstartConfig":
        return cls(
            path=args.path,
            project=args.project,
            html_theme=args.html_theme,
            code_path=args.code_path,
            link_to_github=args.link_to_github,
            version=args.version,
            release=args.release,
        )

    def to_dict(self) -> dict[str, Any]:
        ret = asdict(self)
        ret["path"] = str(self.path)  # Convert to string
        return ret


class Quickstart:
    """
    Quickstart a Certora document project.
    """

    _TEMPLATES = Path(__file__).parent.parent / "templates"
    _ASSETS = Path(__file__).parent.parent / "assets"

    def __init__(self, config: QuickstartConfig):
        self._config = config
        self._path = self._config.path.absolute()

    def _copy_assets(self):
        source = self._path / "source"

        # Copy the logo images to `_static` (the ".png" is needed for latex docs)
        suffixes = {".svg", ".png"}
        for path in self._ASSETS.iterdir():
            if path.suffix in suffixes:
                filename = path.parts[-1]
                static_path = source / f"{self._config.dot}static"
                copyfile(path, static_path / filename)

        # Copy the spelling_wordlist.txt
        spell_path = self._ASSETS / "spelling_wordlist.txt"
        copyfile(spell_path, source / self._config.spelling_word_list_filename)

    def run(self):
        """
        Generate the necessary folder and files.
        """
        d = self._config.to_dict()
        generate(d, overwrite=False, templatedir=str(self._TEMPLATES))
        self._copy_assets()

    @classmethod
    def from_cli_args(cls) -> "Quickstart":
        parser = get_quickstart_parser()
        args = parser.parse_args()
        config = QuickstartConfig.from_args(args)
        return cls(config)


def certora_doc_quickstart():
    quickstart = Quickstart.from_cli_args()
    quickstart.run()
