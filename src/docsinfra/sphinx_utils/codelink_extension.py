"""
A Sphinx extension for linking source code files, either locally or to Github.
"""
import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

from docutils import nodes
from docutils.nodes import Element, Node, system_message
from git import InvalidGitRepositoryError, Repo
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.locale import __
from sphinx.roles import XRefRole
from sphinx.util import logging

logger = logging.getLogger(__name__)


_ROLE_NAME = "clink"


class CodeLinkConfig:
    """
    The configuration needed for code links.
    """

    def __init__(self, env: BuildEnvironment):
        self._env = env
        self._link_to_github = env.config.link_to_github
        self._code_path_override = env.config.code_path_override

        if self.is_codepath_overridden:
            # Calculate the codepath relative to the source dir
            # To use env.relfn2path we need an absolute path
            codepath = self._code_path_override
            if not codepath.startswith("/"):
                codepath = "/" + codepath
            self._code_path_override = Path(env.relfn2path(codepath)[1]).absolute()

    @property
    def is_codepath_overridden(self):
        return self._code_path_override is not None and self._code_path_override != ""

    def get_rel_path(self, path: Path) -> Path:
        """
        Returns path relative to code path.
        """
        if not self.is_codepath_overridden:
            return None
        return path.relative_to(self._code_path_override)

    def get_abs_path(self, path: str) -> Path:
        """
        Returns an absolute path to the file. If the path is relative, or there is
        no code-path override, we use ``BuildEnvironment.relfn2path`` to compute the
        path. Otherwise, the path is considered sa relative to the overridden code path.

        Examples:

        >>> codelinkconfig._code_path_override
        PosixPath('/home/shoham/dev/docs-infrastructure/code')
        >>> codelinkconfig.get_abs_path('voting/Voting_solution.spec')
        PosixPath('/home/shoham/dev/docs-infrastructure/docs/source/voting/Voting_solution.spec')
        """
        pathobj = Path(path)
        if (not self.is_codepath_overridden) or (not pathobj.is_absolute()):
            return Path(self._env.relfn2path(path)[1]).absolute()

        return self._code_path_override / (pathobj.relative_to(pathobj.root))

    @property
    def link_to_github(self) -> bool:
        return self._link_to_github

    @classmethod
    def add_config_values(cls, app: Sphinx):
        """
        Add the config values neede for :class:`.CodeLink`.
        """
        app.add_config_value("code_path_override", None, "env")
        app.add_config_value("link_to_github", True, "env")


class GithubUrlsMaker:
    """
    Computes the url in Github of a given file, returns None if the computation
    failed for any reason.

    .. warning::

        The url is computed by reverse engineering Github's urls. This is prone
        to breaking.

    .. todo:: Cache repositories and their url's.
    """

    def get_repo(self, path: Path) -> Optional[Repo]:
        """
        :return: the path's repository
        """
        try:
            return Repo(path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            return None

    def is_github_url(self, url: str) -> bool:
        """
        Returns whether the given url is in Github.com.
        """
        return re.search(r"\bgithub\.com\b", url) is not None

    def normalize_url(self, url: str) -> str:
        """
        Convert remote repo urls to ``https://`` urls. For example:

        >>> GithubUrlsMaker().normalize_url('git@github.com:Certora/docs-infrastructure.git')
        'https://github.com/Certora/docs-infrastructure/'

        >>> GithubUrlsMaker().normalize_url('https://github.com/Certora/Examples.git')
        'https://github.com/Certora/Examples/'
        """
        if not url.startswith("https://"):
            # Replace ssh access with https
            username, site, rel = re.match(r"(.*)@(.*):(.*).git", url).groups()
            url = f"https://{site}/{rel}"

        if url.endswith(".git"):
            # Remove ".git" ending
            url = url[: -len(".git")]

        if not url.endswith("/"):
            url += "/"
        return url

    def __call__(self, path: Path) -> Optional[str]:
        if not path.exists():
            logger.warning(f"missing {path} - cannot create Github url")
            return None

        repo = self.get_repo(path)
        if repo is None:
            logger.warning(f"no git repo found in {path} - cannot create Github url")
            return None

        url = repo.remote().url
        if not self.is_github_url(url):
            logger.warning(f"repo {repo} is not on Github - cannot create Github url")
            return None

        url = self.normalize_url(url)
        rel_path = path.relative_to(repo.working_dir)
        relative_parts = [
            "tree" if path.is_dir() else "blob",
            repo.head.commit.hexsha,  # Better than using branch
            str(rel_path),
        ]
        relative = "/".join(relative_parts)
        return url + relative


GITHUB_URL_MAKER = GithubUrlsMaker()


class TutorialsCodeLink(XRefRole):
    """
    Sphinx role extension for linking source code files locally in the user's chosen
    code path.
    """

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> tuple[str, str]:
        """
        Called after parsing title and target text, and creating the
        reference node (given in *refnode*).  This method can alter the
        reference node and must return a new (or the same) ``(title, target)``
        tuple.
        """
        config = CodeLinkConfig(env)
        path = config.get_abs_path(target)
        path_link = str(path.as_uri())

        if config.link_to_github:
            url = GITHUB_URL_MAKER(path)
            if url is not None:
                return title, url

            logger.warning(
                __("could not create GitHub link for %s, falling back to local link")
                % target,
            )

        return title, path_link

    def result_nodes(
        self,
        document: nodes.document,
        env: BuildEnvironment,
        node: Element,
        is_ref: bool,
    ) -> tuple[list[Node], list[system_message]]:
        """
        Called before returning the finished nodes.  *node* is the reference
        node if one was created (*is_ref* is then true), else the content node.
        This method can add other nodes and must return a ``(nodes, messages)``
        tuple (the usual return value of a role function).
        """
        config = CodeLinkConfig(env)
        title = str(node.children[0].children[0])
        options = {
            key: node[key] for key in ["refdoc", "refdomain", "reftype", "refexplicit"]
        }
        ref = nodes.reference(
            node.rawsource, title, refuri=node["reftarget"], **options
        )

        # Warn if path is missing
        warnings = []
        path = Path(unquote(urlparse(node["reftarget"]).path))
        if not (config.link_to_github or path.exists()):
            # Leave unresolved
            warn = self.inliner.document.reporter.warning(
                f"Could not resolve link {node.rawsource}, path {path} is missing"
            )
            warnings.append(warn)
        return [ref], warnings


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_role(_ROLE_NAME, TutorialsCodeLink())
    CodeLinkConfig.add_config_values(app)
    return {"version": "0.1", "parallel_read_safe": False}
