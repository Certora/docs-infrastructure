"""
Sphinx extension for linking source code files, either locally or from github.
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
        # Determine code path
        code_path = env.config.code_path
        if code_path is None:
            # Use the source dir
            code_path = ""

        # NOTE: see documentation of relfn2path
        self._code_path = Path(env.relfn2path(code_path)[1])

        # Determine repository
        try:
            self._repo = Repo(self._code_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            self._repo = None

        self._link_to_github = env.config.link_to_github

    @property
    def code_path(self) -> Path:
        return self._code_path

    @property
    def has_repo(self) -> bool:
        return self._repo is not None

    @property
    def code_branch(self) -> Optional[str]:
        if self.has_repo is None:
            return None
        if self._repo.head.is_detached:
            # We need to deduce the branch
            try:
                reference = next(
                    ref
                    for ref in self._repo.references
                    if ref.commit == self._repo.head.commit
                )
                return reference.remote_head
            except StopIteration:
                return None
        return self._repo.active_branch.name

    @property
    def code_repo_url(self) -> Optional[str]:
        if not self.has_repo:
            return None
        return self._repo.remote().url

    @property
    def repo_root(self) -> Optional[Path]:
        if not self.has_repo:
            return None
        return Path(self._repo.git_dir).parent

    @property
    def link_to_github(self) -> bool:
        return self._link_to_github

    @classmethod
    def add_config_values(cls, app: Sphinx):
        """
        Add the config values neede for :class:`.CodeLink`.
        """
        app.add_config_value("code_path", None, "env")
        app.add_config_value("link_to_github", True, "env")


class GithubUrlsMaker:
    """
    If the package is installed using ``pip3 install -e``, the current file is in
    path <repo-root>/src/tutorials/sphinx_utils/codelink_extension.py. From this and the
    current barnch, we can deduce the github url.

    Otherwise, we'll assume the current branch is master.
    """

    def __init__(self, conf: CodeLinkConfig):
        self._repo_root = conf.repo_root

        if conf.code_branch is None:
            raise ValueError("Missing code branch - cannot deduce github link")
        self._branch = conf.code_branch

        if conf.code_repo_url is None:
            raise ValueError("Missing code remote url - cannot deduce github link")
        url = conf.code_repo_url
        if not url.startswith("https://"):
            # Replace ssh access with https
            username, site, rel = re.match(r"(.*)@(.*):(.*).git", url).groups()
            url = f"https://{site}/{rel}"

        self._url = url

    def get_github_link(self, path: Path) -> str:
        # TODO: The building of the github link is by reverse engineering
        base = self._url
        if not base.endswith("/"):
            base += "/"

        rel_path = path.relative_to(self._repo_root)
        relative_parts = [
            "tree" if path.is_dir() else "blob",
            self._branch,
            str(rel_path),
        ]
        relative = "/".join(relative_parts)
        return base + relative


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
        path = config.code_path / target
        url = str(path.as_uri())

        if config.link_to_github:
            try:
                url = GithubUrlsMaker(config).get_github_link(path)
            except ValueError:
                logger.warning(
                    __(
                        "could not create GitHub link for %s, falling back to local link"
                    )
                    % target,
                )

        return title, url

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
    return {"version": "0.1", "parallel_read_safe": True}
