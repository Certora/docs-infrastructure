"""
Syntax highlighting for CVL2 using :mod:`pygments`.

Sources
-------
Main source:
`Write your own lexer - Pygments <https://pygments.org/docs/lexerdevelopment/>`_.

For pygments tokens see:
`Builtin Tokens <https://pygments.org/docs/tokens/>`_.

For adding a lexer to Sphinx, see:
`<https://github.com/Certora/Documentation/blob/master/conf.py>`_.

For regular expressions, see:
`re - Regular expression operations <https://docs.python.org/3/library/re.html>`_.
"""

from pygments.lexer import RegexLexer, bygroups, include, words
from pygments.token import (Comment, Keyword, Name, Number, Operator,
                            Punctuation, String, Text, Whitespace)

_datatypes_pattern = (
    r"(method|calldataarg|env|mathint|"  # CVL types
    + r"mapping|"  # Added by me
    + r"address|bool|(?:(?:bytes|hash|int|string|uint)(?:8|16|24|32|40|48|56|64"
    + r"|72|80|88|96|104|112|120|128|136|144|152|160|168|176|184|192|200|208"
    + r"|216|224|232|240|248|256)?))"
)


class CVL2Lexer(RegexLexer):
    """
    For Certora Verification Language 2. Based on the :class:`SolidityLexer`.

    Notes:

    * Using `Name.Class` token for contracts
    * Using `Name.Function` token for CVL functions and definitions names

    To add for use by Sphinx, add to the ``conf.py`` file:

    .. code-block:: python

        from tutorials.sphinx_utils import CVL2Lexer

        def setup(sphinx):
            sphinx.add_lexer("cvl", CVL2Lexer)

    To add to pygments lexers for use by other modules (e.g. :mod:`manim`), use the
    following:

    .. code-block:: python

        from tutorials.sphinx_utils import CVL2Lexer
        from pygments.lexers import LEXERS

        LEXERS[CVL2Lexer.__name__] = (
            "tutorials.sphinx_utils",
            CVL2Lexer.name,
            CVL2Lexer.aliases,
            CVL2Lexer.alias_filenames,
            CVL2Lexer.mimetypes,
        )

    This will have the desired result:

    >>> from pygments.lexers import get_lexer_by_name
    >>> get_lexer_by_name("CVL")
    <pygments.lexers.CVL2Lexer>
    """

    # TODO: add CVLDoc comments

    name = "CVL2"
    aliases = ["CVL", "cvl2", "cvl"]
    filenames = ["*.spec"]
    mimetypes = []

    # Helper definitions
    identifier = r"([a-zA-Z_]\w*)"  # Starts with underscore or letter

    summaries = (
        r"\b(ALWAYS|CONSTANT|PER_CALLEE_CONSTANT|NONDET|HAVOC_ECF|HAVOC_ALL|"
        r"DISPATCHER|AUTO)\b"
    )
    summaries_extra = r"\b(UNRESOLVED|ALL|DELETE)\b"
    methods_block_keywords = r"\b(external|internal|returns|envfree|expect)\b"

    hook_special_keywords = r"\b(Sstore|Sload|STORAGE|KEY)\b"

    solidity_keywords = (
        "calldata",
        "else",
        "external",
        "false",
        "for",
        "if",
        "internal",
        "memory",
        "require",
        "return",
        "returns",
        "storage",
        "true",
    )
    cvl_imports = ("as", "import", "use", "using")
    cvl_builtins = ("currentContract", "lastReverted", "lastStorage")
    cvl_assertions = ("assert", "satisfy")
    cvl_keywords = (
        "assuming",
        "axiom",
        "builtin",
        "exists",
        "filtered",
        "forall",
        "havoc",
        "init_state",
        "override",
        "preserved",
        "requireInvariant",
    )
    cvl_modifiers = r"(new|norevert|old|withrevert)\b"
    cvl_declarations = ("persistent",)

    datatype = r"\b" + _datatypes_pattern + r"\b"

    # Tokens
    tokens = {
        "root": [
            include("whitespace"),
            include("comments"),
            #
            # Entering methods block
            # ----------------------
            (
                r"\b(methods)\b(\s*)({)",
                bygroups(Keyword.Reserved, Whitespace, Punctuation),
                "methods_block",
            ),
            #
            # Rules, functions, etc.
            # ----------------------
            (
                r"\b(rule|invariant)(\s+)" + identifier,
                bygroups(Keyword, Whitespace, Name.Class),
            ),
            (
                r"\b(function|definition)(\s+)([a-zA-Z_]\w*)",
                bygroups(Keyword.Type, Whitespace, Name.Function),
            ),
            #
            # Ghosts
            # ------
            (
                # Ghost variable
                r"\b(ghost)\b(\s+)" + datatype,
                bygroups(Keyword.Declaration, Whitespace, Keyword.Type),
            ),
            (
                # Ghost function
                r"\b(ghost)\b(\s+)" + identifier,
                bygroups(Keyword.Declaration, Whitespace, Name.Function),
            ),
            #
            # Hooks
            # -----
            (r"\b(hook)\b", Keyword.Declaration),
            (hook_special_keywords, Keyword.Pseudo),  # TODO: use Name.Builtin instead?
            #
            # Signature
            (
                r"\b(sig)(:)" + identifier + r"\b",
                bygroups(Keyword.Declaration, Operator, Name.Function),
            ),
            #
            # Blockchain related - TODO: remove?
            # ------------------
            (r"\b(msg|block|tx)\.([A-Za-z_][a-zA-Z0-9_]*)\b", Keyword.Constant),
            #
            # Other keywords
            # --------------
            (words(solidity_keywords, prefix=r"\b", suffix=r"\b"), Keyword.Reserved),
            (words(cvl_keywords, prefix=r"\b", suffix=r"\b"), Keyword.Reserved),
            (words(cvl_declarations, prefix=r"\b", suffix=r"\b"), Keyword.Declaration),
            (words(cvl_imports, prefix=r"\b", suffix=r"\b"), Keyword.Namespace),
            (words(cvl_assertions, prefix=r"\b", suffix=r"\b"), Keyword.Reserved),
            (words(cvl_builtins, prefix=r"\b", suffix=r"\b"), Name.Builtin),
            #
            # CVL Modifiers
            (r"@" + cvl_modifiers, Operator.Word),
            #
            # CVL casting
            (r"\b(require|assert)(_)" + _datatypes_pattern + r"\b", Keyword.Reserved),
            (r"\b(to)(_)" + _datatypes_pattern + r"\b", Name.Builtin),
            #
            # Methods block keywords - for inline code highlighting in reStructuredText
            (methods_block_keywords, Keyword.Reserved),
            #
            # Misc
            # ----
            (datatype, Keyword.Type),
            include("constants"),
            include("defaults"),  # Lowest priority
        ],
        "comments": [
            (r"//(\n|[\w\W]*?[^\\]\n)", Comment.Single),
            (r"/(\\\n)?[*][\w\W]*?[*](\\\n)?/", Comment.Multiline),
            (r"/(\\\n)?[*][\w\W]*", Comment.Multiline),
        ],
        "constants": [
            (r'("(\\"|.)*?")', String.Double),
            (r"('(\\'|.)*?')", String.Single),
            (r"\b0[xX][0-9a-fA-F]+\b", Number.Hex),
            (r"\b\d+\b", Number.Decimal),
        ],
        "defaults": [
            (r"[a-zA-Z_]\w*", Text),
            (r"[~!%^&*+=|?:<>/-]", Operator),
            (r"[.;{}(),\[\]]", Punctuation),
        ],
        "whitespace": [(r"\s+", Whitespace), (r"\n", Whitespace)],
        #
        # Inside the methods block
        # ------------------------
        "methods_block": [
            include("whitespace"),
            include("comments"),
            (datatype, Keyword.Type),
            (methods_block_keywords, Keyword.Reserved),
            (summaries_extra, Keyword.Reserved),
            #
            # Functions
            # ---------
            (
                # Function with contract or wildcard
                r"\b(function)(\s+)" + identifier + r"(\.)" + identifier,
                bygroups(
                    Keyword.Declaration,
                    Whitespace,
                    Name.Class,
                    Punctuation,
                    Name.Function,
                ),
            ),
            (
                # Function
                r"\b(function)(\s+)" + identifier,
                bygroups(Keyword.Declaration, Whitespace, Name.Function),
            ),
            #
            # Summaries
            # ---------
            # We do not use Operator token for "=>" in order to
            # differentiate from other uses of the "=>" operator
            (
                r"(=>)(\s+)" + summaries,
                bygroups(Keyword.Pseudo, Whitespace, Keyword.Constant),
            ),
            (  # Summary by function
                r"(=>)(\s+)" + identifier,
                bygroups(Keyword.Pseudo, Whitespace, Name.Function),
            ),
            # Exit methods block
            (r"\}", Punctuation, "#pop"),
            # Msic
            include("constants"),
            include("defaults"),  # Lowest priority
        ],
    }
