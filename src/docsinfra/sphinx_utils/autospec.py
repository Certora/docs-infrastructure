"""
Automatically document specs or spec elements.
"""
from typing import Any

from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective, switch_source_input
from sphinx.util.typing import OptionSpec

from .cvl_domain import CVLModule, _domain, module_name_from_filepath
from .cvlid import CVL_IDS_PARSER, CVLElements

logger = logging.getLogger(__name__)


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
                content = element.documentation_to_rst()
                with switch_source_input(self.state, content):
                    # Any node with children will do, see
                    # https://www.sphinx-doc.org/en/master/extdev/markupapi.html
                    node = Element()
                    self.state.nested_parse(content, 0, node)
                retnodes += node.children

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
