"""
Automatically document specs or spec elements.
"""
from typing import Any, Optional

from cvldoc_parser import AstKind, CvlElement
from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from docutils.statemachine import State, StateMachine, StringList
from sphinx.application import Sphinx
from sphinx.directives.code import container_wrapper
from sphinx.locale import __
from sphinx.util import logging, parselinenos
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec

from .cvl_domain import (MODULE, CVLDomain, CVLModule, CVLObject, _domain,
                         module_name_from_filepath)
from .cvlid import CVL_IDS_PARSER, CVLElements, CVLElemetWrapper

logger = logging.getLogger(__name__)


class CVLElementToArgs:
    """
    Generate a :cvl:`CVLObject` from a :class:`CvlElement`.
    """

    def __init__(
        self,
        element: CVLElemetWrapper,
        filename: Optional[str],
        lineno: int,
        content_offset: int,
        block_text: str,
        state: State,
        state_machine: StateMachine,
    ):
        self._element = element
        self._filename = filename
        self._lineno = lineno
        self._content_offset = content_offset
        self._block_text = block_text
        self._state = state
        self._state_machine = state_machine

    @property
    def directive_name(self) -> str:
        keyword = self._element.keyword
        if keyword not in CVLDomain.directives:
            raise ValueError(f"Unexpected keyword: {keyword}")

        return f"{_domain}:{keyword}"

    @property
    def arguments(self) -> list[str]:
        """
        Returns a single argument which is the signature of the element.
        """
        return [self._element.signature]

    def options(self) -> dict[str, str]:
        ret = {}
        if self._filename is not None:
            ret[MODULE] = self._filename
        return ret

    def content(self) -> StringList:
        return StringList(self._element.documentation_to_rst())

    def generate(self) -> CVLObject:
        return CVLObject(
            name=self.directive_name,
            arguments=self.arguments,
            options=self.options(),
            content=self.content(),
            lineno=self._lineno,
            content_offset=self._content_offset,
            block_text=self._block_text,
            state=self._state,
            state_machine=self._state_machine,
        )


class AutoSpecDoc(SphinxDirective):
    """
    Automatically document spec elements.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: OptionSpec = {
        "tab-width": int,
        "cvlobject": directives.unchanged_required,
        "noindex": directives.flag,  # from CVLModule
        "nocontentsentry": directives.flag,  # from CVLModule
    }

    def run(self) -> list[Node]:
        document = self.state.document
        if not document.settings.file_insertion_enabled:
            return [
                document.reporter.warning("File insertion disabled", line=self.lineno)
            ]

        try:
            # Get location and filename
            location = self.state_machine.get_source_and_line(self.lineno)
            rel_filename, filename = self.env.relfn2path(self.arguments[0])
            self.env.note_dependency(rel_filename)

            # Create module element
            cvl_module = CVLModule(
                name=f"{_domain}:spec",
                arguments=[module_name_from_filepath(filename, self.env)],
                options=self.options,
                content=self.content,
                lineno=self.lineno,
                content_offset=self.content_offset,
                block_text=self.block_text,
                state=self.state,
                state_machine=self.state_machine,
            )
            retnodes = cvl_module.run()

            # desired elements
            cvlobject_option = self.options.get("cvlobject")
            keys = None
            if cvlobject_option is not None and len(cvlobject_option) > 0:
                # Parse the elements ids
                keys, warnings = CVL_IDS_PARSER(cvlobject_option)
                for warning in warnings:
                    logger.warning(__(warning), location=location)

            elements = CVLElements.from_file(filename, raise_on_multiple_matches=True)
            if keys is not None:
                elements = {key: elements.get(key) for key in keys}
                # Warn about missing elements
                for name, element in elements.items():
                    if element is None:
                        logger.warning(
                            __("failed to find CVL element matching %s in %s")
                            % (name, self.filename),
                            location=location,
                        )
                elements = {key: el for key, el in elements.items() if el is not None}

            # Add elements' descriptions
            for element in elements.values():
                generator = CVLElementToArgs(
                    element,
                    filename,
                    self.lineno,
                    self.content_offset,
                    self.block_text,
                    self.state,
                    self.state_machine,
                )
                obj = generator.generate()
                retnodes += obj.run()

            return retnodes
        except Exception as exc:
            return [document.reporter.warning(exc, line=self.lineno)]


def setup(app: Sphinx) -> dict[str, Any]:
    directives.register_directive("autospec", AutoSpecDoc)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
