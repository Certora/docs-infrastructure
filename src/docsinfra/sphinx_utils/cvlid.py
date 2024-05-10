"""
This module provides a wrapper for :class:`CvlElement`.
"""
import re
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple, Optional

from cvldoc_parser import AstKind, CvlElement, DocumentationTag, TagKind, parse
from docutils.statemachine import StringList

from .cvl_domain import _domain

SEPARATOR = ":"


class ParsedCVLKeys(NamedTuple):
    """
    The returned data from :class:`.CVLIdLexer`.
    """

    keys: list[str]
    warnings: list[str]


class CVLIdsParser:
    """
    Parses ``:cvlobject:`` string into individual keys. Needed since we might encounter
    strings such as:
    ``HookSstore@_hasVoted[KEY address voter].structField(offset 32)``.

    **Examples.**

    >>> from docsinfra.sphinx_utils.cvlid import CVLIdsParser
    >>> lxr = CVLIdsParser()
    >>> lxr("numVoted HookSstore:_hasVoted[KEY address voter]")
    ParsedCVLKeys(keys=['numVoted', 'HookSstore:_hasVoted[KEY address voter]'],
    warnings=[])

    >>> lxr("HookSstore:votes[INDEX uin256 i].to(offset 32) Voted")
    ParsedCVLKeys(keys=['HookSstore:votes[INDEX uin256 i].to(offset 32)', 'Voted'],
    warnings=[])

    >>> lxr("HookSstore:voted[INDEX uin256 i numVoted")
    ParsedCVLKeys(keys=['uin256', 'i', 'numVoted'], warnings=['Unclosed ] in option',
    "Syntax error in option[0:23]: 'HookSstore@voted[INDEX '"])
    """

    # Helper definitions
    identifier = r"\b[a-zA-Z_]\w*\b"  # Starts with underscore or letter
    block_parenthesis = r"\[.*?\]"
    normal_parenthesis = r"\(.*?\)"
    dot_identifier = r"\." + identifier

    any_combo = f"({dot_identifier})|({block_parenthesis})|({normal_parenthesis})"

    # Lookahead and lookbehind
    lookbehind = r"((?<=\s)|^)"  # Whitespace or start of string
    lookahead = r"(?=(\s|$))"  # Whitespace or end of string

    regex = (
        f"{lookbehind}{identifier}({SEPARATOR}{identifier}({any_combo})*)?{lookahead}"
    )

    # Parenthesis
    opens_closes = {"(": ")", "[": "]"}
    closes = set(")]")

    def _legal_parenthesis_check(self, line: str) -> Optional[str]:
        """
        Returns ``None`` if parenthesis are legal.
        """
        stack = []
        for i, c in enumerate(line):
            if c in self.opens_closes:
                stack.append(self.opens_closes[c])
            elif c in self.closes:
                if len(stack) > 0 and stack[-1] == c:
                    # Closing matches opening
                    stack.pop(-1)
                else:
                    return f"Unmatched {c} in char {i + 1} of option"

        if len(stack) > 0:
            return f"Unclosed {stack[-1]} in option"

        return None

    def _is_only_whitespace(self, string: str) -> bool:
        return re.fullmatch(r"\s*", string) is not None

    def __call__(self, line: str) -> ParsedCVLKeys:
        """
        :meta public:
        """
        warnings = []
        parenthesis_check = self._legal_parenthesis_check(line)
        if parenthesis_check is not None:
            # We keep trying despite illegal prenthesis
            warnings.append(parenthesis_check)

        matches = list(re.finditer(self.regex, line))

        # Check that in-between matches is only whitespace
        start = 0
        for mtch in matches:
            end = mtch.start()
            string = line[start:end]
            if not self._is_only_whitespace(string):
                warnings.append(f"Syntax error in option[{start}:{end}]: '{string}'")
            start = mtch.end()

        # Check from end of last match to end of string
        string = line[start:]
        if not self._is_only_whitespace(string):
            warnings.append(f"Syntax error in option[{start}:]: '{string}'")

        keys = list(
            line[mtch.start() : mtch.end()]  # noqa
            for mtch in re.finditer(self.regex, line)
        )
        return ParsedCVLKeys(keys, warnings)


CVL_IDS_PARSER = CVLIdsParser()  # A global parser


class StringToKind(Mapping[str, AstKind]):
    """
    Since objects of :class:`cvldoc_parser.AstKind` are not hashable, we use this class
    to get unique strings for them.
    """

    def __init__(self):
        self._kinds = set(
            sorted(name for name in dir(AstKind) if self._is_kind_name(name))
        )

    def _is_kind_name(self, name: str) -> bool:
        return (not name.startswith("_")) and name[0].isupper()

    def __len__(self) -> int:
        return len(self._kinds)

    def __iter__(self):
        for kind_name in self._kinds:
            yield kind_name

    def __getitem__(self, key: str) -> AstKind:
        try:
            return getattr(AstKind, key)
        except AttributeError:
            raise KeyError(key)

    def kind_to_str(self, kind: AstKind):
        """
        :meta public:
        """
        try:
            return next(name for name in self if getattr(AstKind, name) == kind)
        except StopIteration:
            raise ValueError(f"Unknown kind {kind}")


_KIND_CONVERTER = StringToKind()


class StringToTag(Mapping[str, TagKind]):
    """
    Since objects of :class:`cvldoc_parser.TagKind` are not hashable, we use this class
    to get unique strings for them. These objects describe documentation tags.
    """

    def __init__(self):
        self._tags = set(
            sorted(name for name in dir(TagKind) if self._is_tag_name(name))
        )

    def _is_tag_name(self, name: str) -> bool:
        return (not name.startswith("_")) and name[0].isupper()

    def __len__(self) -> int:
        return len(self._tags)

    def __iter__(self):
        for tag_name in self._tags:
            yield tag_name

    def __getitem__(self, key: str) -> TagKind:
        try:
            return getattr(TagKind, key)
        except AttributeError:
            raise KeyError(key)

    def tag_to_str(self, tag: TagKind):
        """
        :meta public:
        """
        try:
            return next(name for name in self if getattr(tag, name) == tag)
        except StopIteration:
            raise ValueError(f"Unknown tag {tag}")


_TAG_CONVERTER = StringToTag()


class IndexToLine:
    """
    This class is for translating an index in a file to the line number. This is needed
    because a :class:`CvlElement` provides its span only in terms of character index,
    and not the line numbers used by :mod:`Sphinx` for location.

    This class is callable, returning the line number for a given character index.
    """

    def __init__(self, path: Path):
        self._path = path
        with open(path) as f:
            text = f.read()

        # Calculate the cumulative line length
        cur_sum = 0
        self._cum_length = []
        for line in text.splitlines(keepends=True):
            cur_sum += len(line)
            self._cum_length.append(cur_sum)

    @property
    def path(self) -> Path:
        return self._path

    def __call__(self, char_index: int) -> int:
        try:
            index = next(
                i for i, cumsum in enumerate(self._cum_length) if cumsum > char_index
            )
            return index + 1  # Line numbers start at 1
        except StopIteration:
            return len(self._cum_length) + 1


class CVLElemetWrapper:
    """
    Wraps :class:`CvlElement` and provides additional functions such as
    getting the element's signature. In addition treats any text after an empty line
    following the last tag as free description text.
    """

    _SEPARATOR = SEPARATOR  # Using the global separator
    _RST_TAB_LENGTH = 3  # Three spaces in reStructuredText

    _UNIQUE_KINDS = {"Methods": "methods"}

    # Kinds that are always identified by name
    _NAMED_KINDS = {
        "Definition",
        "Function",
        "GhostFunction",
        "GhostMapping",
        "Invariant",
        "Rule",
    }

    # Kinds that require additional data to be identified, and the data field's name
    _EXTRA_DATA_KINDS = {
        "HookOpcode": "opcode",
        "HookSload": "slot_pattern",
        "HookSstore": "slot_pattern",
    }

    _KIND_TO_KEYWORD = {
        "Definition": "definition",
        "Function": "function",
        "GhostFunction": "ghost",
        "GhostMapping": "ghost",
        "Invariant": "invariant",
        "Rule": "rule",
        "HookOpcode": "hook",
        "HookSload": "hook Sload",
        "HookSstore": "hook Sstore",
    }

    def __init__(
        self, element: CvlElement, index_to_line: Optional[IndexToLine] = None
    ):
        self._element = element
        if self.kind_name not in self.supported_kinds():
            raise ValueError(f"Unsupported element kind {element}")
        self._index_to_line = index_to_line

    @classmethod
    def supported_kinds(cls) -> list[str]:
        """
        A list of all supported :class:`AstKind`.
        """
        return (
            list(cls._UNIQUE_KINDS)
            + list(cls._NAMED_KINDS)
            + list(cls._EXTRA_DATA_KINDS)
        )

    @property
    def kind_name(self) -> str:
        return _KIND_CONVERTER.kind_to_str(self._element.ast.kind)

    @property
    def keyword(self) -> str:
        return self._KIND_TO_KEYWORD[self.kind_name]

    @property
    def to_key(self) -> str:
        kind_name = self.kind_name
        if kind_name in self._UNIQUE_KINDS:
            return kind_name

        if kind_name in self._NAMED_KINDS:
            return self._element.element_name()

        if kind_name in self._EXTRA_DATA_KINDS:
            extra = self._element.ast.data[self._EXTRA_DATA_KINDS[kind_name]]
            return f"{kind_name}{self._SEPARATOR}{extra}"
        raise ValueError(f"Unexpected CVL kind {kind_name}")

    @property
    def signature(self) -> str:
        kind_name = self.kind_name
        if kind_name in self._UNIQUE_KINDS:
            # E.g. "methods"
            return kind_name

        def get_param(param: dict[str, str]) -> str:
            name = param["name"]
            param_type = param["ty"]
            return f"{param_type} {name}"

        if kind_name in self._NAMED_KINDS:
            name = self._element.element_name()
            params = self._element.ast.data.get("params")
            if params is not None:
                params = ", ".join(get_param(par) for par in params)
            else:
                params = ""
            return f"{name}({params})"

        if kind_name in self._EXTRA_DATA_KINDS:
            extra = self._element.ast.data[self._EXTRA_DATA_KINDS[kind_name]]
            return f"{extra}"

        raise ValueError(f"Unexpected CVL kind {kind_name}")

    @property
    def lines_span(self) -> tuple[int, int]:
        """
        The start and end lines of the element.
        """
        span = self._element.span()
        return (self._index_to_line(span.start), self._index_to_line(span.end))

    def documentation_to_rst(self) -> StringList:
        r"""
        Translates the CVL "natspec" to restructuredText format, as a list of lines.
        If there is text following an empty line in the last tag, it is treated as
        free text.

        For example, the following CVL spec code:

        .. code-block:: cvl

           /** @title Voter determines if vote in favor or against
            *  @notice Notice something amazing, can this span multiple lines and paragraphs? We'll
            *  just have to check. No multiple paragraphs.
            *  But we can do inline math :math:`x + y \leq z`!
            *  @param isInFavor for or against the proposal
            *  @return This is a rule, it has no return value!
            *
            *  Free text follows an empty line after the last tag.
            *  This can even include nested content -- but note that `cvldoc` removes spaces, which
            *  will cause issues.
            */

        Will be converted to a :class:`StringList` equivalent to the following lines:

        .. code-block:: restructuredtext

           .. cvl:rule:: voterDecides(bool isInFavor)

              :title: Voter determines if vote in favor or against
              :notice: Notice something amazing, can this span multiple lines and paragraphs? We'll
                 just have to check. No multiple paragraphs.
                 But we can do inline math :math:`x + y \leq z`!
              :param isInFavor: for or against the proposal
              :return: This is a rule, it has no return value!

              Free text follows an empty line after the last tag.
              This can even include nested content -- but note that `cvldoc` removes spaces, which
              will cause issues.

        """
        tab = " " * self._RST_TAB_LENGTH
        lines = StringList()
        source = str(self._index_to_line.path)
        first_line, _ = self.lines_span

        def divide_by_first_empty_line(desc: str) -> tuple[str, str]:
            """
            Returns the string before the first empty and after.
            """
            lines = desc.splitlines()
            try:
                first_empty_line = next(
                    i for i, line in enumerate(lines) if line.strip() == ""
                )
            except StopIteration:
                return (desc, "")

            first_part = "\n".join(lines[:first_empty_line])
            second_part = "\n".join(lines[first_empty_line:])
            return (first_part, second_part)

        def doctag_to_rst(doctag: DocumentationTag, is_last: bool = False) -> list[str]:
            if doctag.kind == TagKind.Param:
                desc = doctag.param_name_and_description()
                if desc is not None:
                    name, desc = desc
                    if name.endswith(":"):
                        name = name[:-1]
                    desc = desc.splitlines()
                    prefix = f"{tab}:param {name}: "
                else:
                    raise ValueError(f"Unexpected documentation tag: {doctag}")
            else:
                tagname = _TAG_CONVERTER.tag_to_str(doctag.kind).lower()
                desc = doctag.description
                if is_last:
                    # Ignore everything after empty line
                    desc, _ = divide_by_first_empty_line(desc)
                desc = desc.splitlines()
                prefix = f"{tab}:{tagname}: "
            return [prefix + desc[0]] + [2 * tab + dline for dline in desc[1:]]

        # Parse all tags but the last.
        line = first_line
        num_tags = len(self._element.doc)
        for i, doctag in enumerate(self._element.doc):
            rst_lines = doctag_to_rst(doctag, is_last=i == num_tags - 1)
            for rst_line in rst_lines:
                lines.append(rst_line, source, line)
                line += 1

        # Add free text after last tag
        last_tag = self._element.doc[-1]
        _, free_text = divide_by_first_empty_line(last_tag.description)
        if free_text != "":
            for text_line in free_text.splitlines():
                lines.append(tab + text_line, source, line)
                line += 1

        # First line is the directive, in the source it comes after the doc elements.
        directive = f".. {_domain}:{self.keyword}:: {self.signature}"
        lines.insert(0, directive, source, line)
        lines.insert(1, "", source, line + 1)  # Empty line before fields

        # TODO Below is a HACK. Sphinx seems to double the last line, so we add an empty
        # line at the end
        lines.append("", source)

        return lines

    def raw(self) -> str:
        return self._element.raw()

    def _parse_key(self, key: str) -> tuple[Optional[str], str]:
        """
        Key is either an element name, or a kind name and some string separated by
        the _SEPARATOR, i.e. "<kind name>:<string>".

        :return: the kind name and the additional string
        """
        if self._SEPARATOR not in key:
            return None, key

        if key.count(self._SEPARATOR) != 1:
            raise ValueError(
                f"Malformed CVL element identifier {key} - use only one {self._SEPARATOR}"
            )

        kind_name, data = key.split(self._SEPARATOR)
        if kind_name not in _KIND_CONVERTER:
            raise ValueError(f"Unknown kind {kind_name} in {key}")

        return kind_name, data

    def is_identifier_of(self, key: str) -> bool:
        """
        :meta public:
        """
        key_kind_name, name = self._parse_key(key)

        kind_name = self.kind_name

        if kind_name in self._UNIQUE_KINDS:
            # This is for the methods block
            unique_name = self._UNIQUE_KINDS[kind_name]
            valid_names = {unique_name, kind_name}
            return name in valid_names and (
                (key_kind_name is None) or (key_kind_name == kind_name)
            )

        if kind_name in self._NAMED_KINDS:
            return name == self._element.element_name() and (
                (key_kind_name is None) or (key_kind_name == kind_name)
            )

        if kind_name in self._EXTRA_DATA_KINDS:
            if key_kind_name is None:
                return False  # Cannot deduce kind from key
            extra = self._element.ast.data[self._EXTRA_DATA_KINDS[kind_name]]
            return (key_kind_name == kind_name) and (extra == name)

        return False


class CVLElements(Mapping[str, CVLElemetWrapper]):
    """
    Provides a mapping between CVL element's ids and the elements.
    """

    def __init__(
        self, filename: str, elements: list[CvlElement], raise_on_multiple_matches: bool
    ):
        path = Path(filename)
        index_to_line = IndexToLine(path)
        self._elements = [CVLElemetWrapper(e, index_to_line) for e in elements]
        self._raise_on_multiple_matches = raise_on_multiple_matches

    @classmethod
    def from_file(cls, filename: str, raise_on_multiple_matches: bool) -> "CVLElements":
        try:
            parsed = parse(filename)
        except ValueError:
            raise ValueError(f"CVLDoc failed to parse {filename}")

        if len(parsed) == 0:
            raise ValueError(f"CVLDoc returned no elements for {filename}")

        return cls(filename, parsed, raise_on_multiple_matches)

    def __len__(self) -> int:
        return len(self)

    def __iter__(self):
        for element in self._elements:
            yield element.to_key

    def __getitem__(self, key: str) -> CvlElement:
        matches = [el for el in self._elements if el.is_identifier_of(key)]
        if len(matches) == 0:
            raise KeyError(key)
        if len(matches) > 1 and self._raise_on_multiple_matches:
            raise ValueError(f"Found several elements matching {key} in {self._name}")
        # Use the first one
        return matches[0]
