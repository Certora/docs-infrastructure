"""
Adds index types for CVL.
"""
from typing import Iterable

from sphinx.domains import Index, IndexEntry
from sphinx.locale import _


class RuleIndex(Index):
    """
    Custom index by rule name.
    """

    name = "ruleindex"
    localname = _("Rule Index")
    shortname = _("rules")
    _object_types = {"rule", "invariant"}

    def generate(
        self, docnames: Iterable[str] | None = None
    ) -> tuple[list[tuple[str, list[IndexEntry]]], bool]:
        """
        Get entries for the index.

        If ``docnames`` is given, restrict to entries referring to these
        docnames.

        The return value is a tuple of ``(content, collapse)``:

        ``collapse``
          A boolean that determines if sub-entries should start collapsed (for
          output formats that support collapsing sub-entries).

        ``content``:
          A sequence of ``(letter, entries)`` tuples, where ``letter`` is the
          "heading" for the given ``entries``, usually the starting letter, and
          ``entries`` is a sequence of single entries. Each entry is a sequence
          ``[name, subtype, docname, anchor, extra, qualifier, descr]``. The
          items in this sequence have the following meaning:

          ``name``
            The name of the index entry to be displayed.

          ``subtype``
            The sub-entry related type. One of:

            ``0``
              A normal entry.
            ``1``
              An entry with sub-entries.
            ``2``
              A sub-entry.

          ``docname``
            *docname* where the entry is located.

          ``anchor``
            Anchor for the entry within ``docname``

          ``extra``
            Extra info for the entry.
            In *furo* theme it appears in parenthesis after the entry, before ``descr``.

          ``qualifier``
            Qualifier for the description.
            In *furo* theme it appears as ``qualifier: descr``

          ``descr``
            Description for the entry.

        Qualifier and description are not rendered for some output formats such
        as LaTeX.
        """
        rules = [
            (refname, dispname, docname, anchor, typ)
            for refname, dispname, typ, docname, anchor, _ in self.domain.get_objects()
            if typ in self._object_types
        ]
        if docnames is not None:
            rules = [rule for rule in rules if rule[1] in docnames]
        rules = sorted(rules)

        content = {}
        for refname, dispname, docname, anchor, typ in rules:
            letter_content = content.setdefault(dispname[0].lower(), [])

            qualifier = ""
            if refname != dispname:
                qualifier = self.domain.get_specname(refname)
                if qualifier is None:
                    qualifier = ""

            letter_content.append(
                (
                    dispname,
                    0,
                    docname,
                    anchor,
                    "",
                    qualifier,
                    typ,
                )
            )

        content = sorted(content.items())
        return content, False


class SpecIndex(Index):
    """
    Custom index for spec files.
    """

    name = "specindex"
    localname = _("Spec File Index")
    shortname = _("specs")

    def generate(
        self, docnames: Iterable[str] | None = None
    ) -> tuple[list[tuple[str, list[IndexEntry]]], bool]:
        specs = sorted(self.domain.data["specs"].items())
        objects = {
            refname: (dispname, docname, anchor, typ)
            for refname, dispname, typ, docname, anchor, _ in self.domain.get_objects()
        }

        content = {}
        for spec_name, spec_entry in specs:
            letter = spec_name[0].lower() if spec_name[0].isalpha() else spec_name[1]
            letter_content = content.setdefault(letter, [])
            if spec_entry.has_spec_object:
                dispname, docname, anchor, typ = objects[spec_name]
                # TODO: dispname unused
                letter_content.append(
                    (
                        spec_name,
                        1,
                        docname,
                        anchor,
                        "",
                        "",
                        "",
                    )
                )
            else:
                letter_content.append((spec_name, 1, "", "", "", "", ""))
            for refname in sorted(spec_entry.rules_refnames):
                dispname, docname, anchor, typ = objects[refname]
                letter_content.append((dispname, 2, docname, anchor, "", "", typ))

        content = sorted(content.items())
        return content, False


class PropertyIndex(Index):
    """
    Custom index for properties.
    """

    name = "propertyindex"
    localname = _("Property Index")
    shortname = _("properties")

    def generate(
        self, docnames: Iterable[str] | None = None
    ) -> tuple[list[tuple[str, list[IndexEntry]]], bool]:
        # TODO: Add rules that are also independent properties
        # TODO: Add all rules referring to a property
        properties = [
            (dispname, docname, anchor, typ)
            for _, dispname, typ, docname, anchor, _ in self.domain.get_objects()
            if typ == "property"
        ]
        if docnames is not None:
            properties = [prop for prop in properties if prop[1] in docnames]
        properties = sorted(properties)

        content = {}
        for dispname, docname, anchor, typ in properties:
            letter_content = content.setdefault(dispname[0].lower(), [])
            letter_content.append(
                (
                    dispname,
                    0,
                    docname,
                    anchor,
                    docname,  # TODO: what is this "extra"
                    "",  # TODO: What is the "qualifier"
                    "",
                )
            )

        content = sorted(content.items())
        return content, False
