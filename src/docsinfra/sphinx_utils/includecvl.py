"""
A Sphinx extension which adds a Sphinx directive for including CVL snippets from
spec files.
"""
from pathlib import Path
from typing import Any

from cvldoc_parser import CvlElement, parse
from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.directives.code import (LiteralInclude, LiteralIncludeReader,
                                    container_wrapper)
from sphinx.locale import __
from sphinx.util import logging, parselinenos

from .codelink_extension import CodeLinkConfig

logger = logging.getLogger(__name__)

_INVALID_OPTIONS_PAIR = LiteralIncludeReader.INVALID_OPTIONS_PAIR + [
    ("diff", "cvlobject"),
    ("pyobject", "cvlobject"),
]


# TODO: Enable replacing some lines by ellipsis
# TODO: Hooks are currently ignored by cvldoc_parser, once fixed enable extracting them
class CVLIncludeReader(LiteralIncludeReader):
    """
    Extends :class:`sphinx.directives.code.LiteralIncludeReader` by allowing to
    extract CVL elements in spec files by name.

    * By default, the language used is CVL.
    * Currently does *not* support both ``diff`` together with ``cvlobject``
      (for showing the diff for a particular object).
    """

    INVALID_OPTIONS_PAIR = _INVALID_OPTIONS_PAIR
    METHODS = "methods"
    SPACING = "spacing"
    _default_spacing = 1  # Single line spacing between elements

    def read(self, location: tuple[str, int] | None = None) -> tuple[str, int]:
        if "diff" in self.options:
            lines = self.show_diff()
        else:
            filters = [
                self.pyobject_filter,
                self.cvlobject_filter,
                self.start_filter,
                self.end_filter,
                self.lines_filter,
                self.dedent_filter,
                self.prepend_filter,
                self.append_filter,
            ]
            lines = self.read_file(self.filename, location=location)
            for func in filters:
                lines = func(lines, location=location)

        return "".join(lines), len(lines)

    def _get_cvlelement_name(self, cvlelement: CvlElement) -> str:
        """
        :return: the name of the element, or ``self.METHODS`` if this element is the
            methods block
        """
        name = cvlelement.ast.name
        if name is None and cvlelement.ast.kind == self.METHODS:
            # The methods block
            name = self.METHODS
        return name

    def cvlobject_filter(
        self, lines: list[str], location: tuple[str, int] | None = None
    ) -> list[str]:
        cvlobjects = self.options.get("cvlobject")
        spacing_lines = self.options.get(self.SPACING, self._default_spacing) + 1

        # Set the language
        if self.options.get("language") is None:
            self.options["language"] = "cvl"

        if cvlobjects:
            try:
                # TODO: Since `parse` only accepts filenames, we reread the file.
                # Should fix this hack once `cvldoc_parser.parse` accepts strings.
                parsed = parse([self.filename])
            except ValueError:
                raise ValueError(f"CVLDoc failed to parse {self.filename}")

            parsed = parsed[0]  # only a single file was parsed
            if len(parsed) == 0:
                raise ValueError(f"CVLDoc returned no elements for {self.filename}")

            cvlobjects = cvlobjects.split()  # Accept a list of cvl objects
            cvls = dict.fromkeys(cvlobjects)  # Keep the order

            for cvlelement in parsed:
                name = self._get_cvlelement_name(cvlelement)
                if name in cvls:
                    if cvls[name] is not None:
                        raise ValueError(
                            f"Found two elements matching {name} in {self.filename}"
                        )
                    cvls[name] = cvlelement.raw()

            # Warn about missing elements
            for name, element in cvls.items():
                if element is None:
                    logger.warning(
                        __("failed to find CVL element matching %s in %s")
                        % (name, self.filename),
                        location=location,
                    )

            # Remove missing elements
            cvls = {name: el for name, el in cvls.items() if el is not None}

            spacing = "\n" * spacing_lines
            text = spacing.join(cvls.values())
            lines = text.splitlines(True)
        return lines


# Extend the option_spec with new options
_extended_option_spec = dict(LiteralInclude.option_spec)
_extended_option_spec["cvlobject"] = directives.unchanged_required
_extended_option_spec[CVLIncludeReader.SPACING] = int


class CVLInclude(LiteralInclude):
    """
    Extends :class:`sphinx.directives.code.LiteralInclude`.

    #. Enables including CVL elements by name. To include cvl elements by name use the
       ``cvlobject`` option and provide a list of CVL elements names, separated by
       spaces. To include the methods block use ``methods``.
       Also adds the ``spacing`` option which determines the number of lines between CVL
       elements.
    #. Automatically determines the language for certain file extensions using the
       :attr:`~docsinfra.sphinx_utils.includecvl.CVLInclude.file_suffix_to_language`
       class variable.
    #. Changes the default caption to use a code link (``:clink:`` role) to the
       relevant file. The *default caption* is used whenever there is an empty
       ``:caption:`` caption option.
    """

    option_spec = _extended_option_spec

    file_suffix_to_language = {".spec": "cvl", ".sol": "solidity", ".conf": "json"}
    """ Default languages to use for these suffixes. """

    def _default_caption(self) -> str:
        """
        The default caption is a ``:clink:`` to the file, with name being the
        file name.
        """
        name = Path(self.arguments[0]).parts[-1]
        return f":clink:`{name}<{self.arguments[0]}>`"

    # NOTE: This is modified from LiteralInclude.run
    def run(self) -> list[Node]:
        document = self.state.document
        if not document.settings.file_insertion_enabled:
            return [
                document.reporter.warning("File insertion disabled", line=self.lineno)
            ]
        # convert options['diff'] to absolute path
        if "diff" in self.options:
            _, path = self.env.relfn2path(self.options["diff"])
            self.options["diff"] = path

        try:
            location = self.state_machine.get_source_and_line(self.lineno)

            # Using CodeLinkConfig to get file paths instead of self.env.relfn2path
            codelink = CodeLinkConfig(self.env)
            rel_filename, filename = codelink.relfn2path(self.arguments[0])
            self.env.note_dependency(rel_filename)

            # Set language based on extension
            if ("language" not in self.options) and ("diff" not in self.options):
                suffix = Path(filename).suffix
                if suffix in self.file_suffix_to_language:
                    self.options["language"] = self.file_suffix_to_language[suffix]

            reader = CVLIncludeReader(filename, self.options, self.config)
            text, lines = reader.read(location=location)

            retnode: Element = nodes.literal_block(text, text, source=filename)
            retnode["force"] = "force" in self.options
            self.set_source_info(retnode)
            if self.options.get("diff"):  # if diff is set, set udiff
                retnode["language"] = "udiff"
            elif "language" in self.options:
                retnode["language"] = self.options["language"]
            if (
                "linenos" in self.options
                or "lineno-start" in self.options
                or "lineno-match" in self.options
            ):
                retnode["linenos"] = True
            retnode["classes"] += self.options.get("class", [])
            extra_args = retnode["highlight_args"] = {}
            if "emphasize-lines" in self.options:
                hl_lines = parselinenos(self.options["emphasize-lines"], lines)
                if any(i >= lines for i in hl_lines):
                    logger.warning(
                        __("line number spec is out of range(1-%d): %r")
                        % (lines, self.options["emphasize-lines"]),
                        location=location,
                    )
                extra_args["hl_lines"] = [x + 1 for x in hl_lines if x < lines]
            extra_args["linenostart"] = reader.lineno_start

            if "caption" in self.options:
                caption = self.options["caption"]
                # Use default caption if caption is empty
                if caption is None or len(caption) == 0:
                    caption = self._default_caption()
                retnode = container_wrapper(self, retnode, caption)

            # retnode will be note_implicit_target that is linked from caption and numref.
            # when options['name'] is provided, it should be primary ID.
            self.add_name(retnode)

            return [retnode]
        except Exception as exc:
            return [document.reporter.warning(exc, line=self.lineno)]


def setup(app: Sphinx) -> dict[str, Any]:
    directives.register_directive("cvlinclude", CVLInclude)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
