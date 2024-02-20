"""
This module determines the syntax for identifying a CVL element in a given spec.
It has two main classes:

#. :class:`.CVLIdsParser` -- for parsing the cvl elements' ids from the ``:cvlobject:``
   option
#. :class:`.CVLIdentifier` -- for identifying if a :class:`~cvldoc_parser.CvlElement`
   matches a given id
"""
import re
from collections.abc import Mapping
from typing import NamedTuple, Optional

from cvldoc_parser import AstKind, CvlElement

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
    >>> lxr("numVoted HookSstore@_hasVoted[KEY address voter]")
    ParsedCVLKeys(keys=['numVoted', 'HookSstore@_hasVoted[KEY address voter]'],
    warnings=[])

    >>> lxr("HookSstore@votes[INDEX uin256 i].to(offset 32) Voted")
    ParsedCVLKeys(keys=['HookSstore@votes[INDEX uin256 i].to(offset 32)', 'Voted'],
    warnings=[])

    >>> lxr("HookSstore@voted[INDEX uin256 i numVoted")
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


class CVLIdentifier:
    """
    Identifies if a given id key matches a given :class:`~cvldoc_parser.CvlElement`.
    """

    _SEPARATOR = SEPARATOR  # Using the global separator

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

    def __init__(self):
        self._kind_converter = StringToKind()

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
        if kind_name not in self._kind_converter:
            raise ValueError(f"Unknown kind {kind_name} in {key}")

        return kind_name, data

    def is_identifier_of(self, key: str, element: CvlElement) -> bool:
        """
        :meta public:
        """
        key_kind_name, name = self._parse_key(key)

        kind = element.ast.kind
        kind_name = self._kind_converter.kind_to_str(kind)

        if kind_name in self._UNIQUE_KINDS:
            # This is for the methods block
            unique_name = self._UNIQUE_KINDS[kind_name]
            valid_names = {unique_name, kind_name}
            return name in valid_names and (
                (key_kind_name is None) or (key_kind_name == kind_name)
            )

        if kind_name in self._NAMED_KINDS:
            return name == element.element_name() and (
                (key_kind_name is None) or (key_kind_name == kind_name)
            )

        if kind_name in self._EXTRA_DATA_KINDS:
            if key_kind_name is None:
                return False  # Cannot deduce kind from key
            extra = element.ast.data[self._EXTRA_DATA_KINDS[kind_name]]
            return (key_kind_name == kind_name) and (extra == name)

        return False
