"""
Defines a CVL domain for Sphinx. A Domain is meant to be a group of "object" description
directives for objects of a similar nature, and corresponding roles to create references
to them.
"""
import re
from pathlib import Path
from typing import Any, Iterable, NamedTuple, Optional, Union, cast

from docutils import nodes
from docutils.nodes import Element, Node, reference
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.addnodes import desc_signature, pending_xref
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.locale import _, __
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import (find_pending_xref_condition, make_id,
                               make_refnode, nested_parse_with_titles)
from sphinx.util.typing import OptionSpec

from .codelink_extension import CodeLinkConfig
from .cvl_index import PropertyIndex, RuleIndex, SpecIndex

logger = logging.getLogger(__name__)


# ==============================================================================
# Constants
# ==============================================================================
SPECFILE = "spec"
_domain = "cvl"
_curspec_key = f"{_domain}:{SPECFILE}"
_kind_key = f"{_domain}:kind"  # For object type (aka kind)
_spec_separator = ":"

cvl_identifier = r"([a-zA-Z_]\w*)"  # Starts with underscore or letter
_max_sig_single_line_len = 80

_cvl_object_types: dict[str, ObjType] = {
    "rule": ObjType(_("rule"), "rule"),
    "invariant": ObjType(_("invariant"), "invariant"),
    "function": ObjType(_("function"), "function"),
    "definition": ObjType(_("definition"), "definition"),
    "hook": ObjType(_("hook"), "hook"),
    "ghost": ObjType(_("ghost"), "ghost"),
    "methods": ObjType(_("methods"), "methods"),
    "spec": ObjType(_("spec"), "spec"),  # Spec file
    "property": ObjType(_("property"), "property"),
}


# ==============================================================================
# Naming functions
# ==============================================================================
def canonical_spec_link_from_filepath(
    filepath: Optional[Union[str, Path]], env: BuildEnvironment
) -> Optional[str]:
    """
    Returns the shortest relative path for the spec file using the remappings if
    possible. This is the canonical spec name.

    :param filepath: a path to the spec file
    """
    if filepath is None:
        return None

    path = Path(filepath)

    # Use path relative to code path or remappings
    code_conf = CodeLinkConfig(env)
    path = code_conf.path2relfn(path)
    return path


def canonical_spec_name_from_filepath(
    filepath: Union[str, Path], env: BuildEnvironment
) -> str:
    """
    The canonical spec name.
    """
    return str(canonical_spec_link_from_filepath(filepath, env))


def to_refname(reftype: str, spec_name: Optional[str], rule_name: Optional[str]) -> str:
    """
    Generate a full name (reference name) for a rule or invariant.

    .. important::

        The ``spec_name`` must be the canonical spec name.

    :param reftype: one of ``CVLDomain.object_types.keys()``
    :param spec_name: the *canonical spec name* (using canonical_spec_link_from_filepath)
    :param rule_name: rule or property name
    """
    if reftype == "spec":
        assert rule_name is None
        assert spec_name is not None
        parts = (_domain, reftype, spec_name)
    elif spec_name is None:
        if rule_name is None:
            raise ValueError("Empty spec and rule/property name")
        parts = (_domain, reftype, rule_name)
    else:
        parts = (_domain, reftype, spec_name, rule_name)
    return _spec_separator.join(parts)


def spec_and_rulename_from_ref(
    refname: str, reftype: str
) -> tuple[str, Optional[str], Optional[str]]:
    """
    Separates the spec name and rule name from the full name (reference name).
    Returns object type, spec name and rule or property name.

    :param reftype: one of ``CVLDomain.object_types.keys()`` (object kind)
    :raise ValueError: if ``refname`` is not a valid rule ref
    """
    if len(refname) == 0:
        raise ValueError("Unexpected empty full name in CVL domain")
    parts = refname.split(_spec_separator)

    if len(parts) < 3:
        raise ValueError(
            f"Unexpected full name in CVL domain {refname} - too few parts"
        )
    if parts[0] != _domain:
        raise ValueError(f"Unexpected full name in CVL domain {refname} - wrong domain")
    if parts[1] not in _cvl_object_types:
        raise ValueError(f"Unexpected full name in CVL domain {refname} - wrong type")

    if reftype == "spec":
        if len(parts) > 3:
            raise ValueError(
                f"Unexpected full name in CVL domain {refname} - "
                "spec should have 3 parts"
            )
        return reftype, parts[2], None
    if reftype == "property":
        if len(parts) > 3:
            raise ValueError(
                f"Unexpected full name in CVL domain {refname} - "
                "property should have 3 parts"
            )
        return reftype, None, parts[2]

    if len(parts) == 3:
        # No spec file
        return reftype, None, parts[2]

    if len(parts) > 4:
        raise ValueError(
            f"Unexpected full name in CVL domain {refname} - too many parts"
        )
    return reftype, parts[2], parts[3]


def canonical_spec_and_rulename_from_target(
    target: str, reftype: str, env: BuildEnvironment
) -> tuple[Optional[str], str]:
    """
    Separates the spec name and rule name from the full name (reference name).
    Returns the *canonical spec name* (if relevant) and the rule or property name.

    :param reftype: one of ``CVLDomain.object_types.keys()``
    """
    _, specname, rulename = spec_and_rulename_from_ref(target, reftype)
    if specname is not None:
        specname = canonical_spec_name_from_filepath(specname)
    return specname, rulename


# ==============================================================================
# CVL directives and roles
# ==============================================================================
class CVLObjectEntry(NamedTuple):
    docname: str  # The document where it is to be found.
    node_id: str  # The anchor name for the object.
    objtype: str  # Object type, a key in ``CVLDomain.object_types``, aka ``kind``


class CVLSpecEntry(NamedTuple):
    """
    The main spec mention and rules in the spec.
    """

    has_spec_object: bool
    rules_refnames: list[str]


class CVLXRefRole(XRefRole):
    """
    Roles for cross-referencing cvl domain directives. Examples:

    * ``:cvl:rule:`@voting/Voting_solution.spec:anyoneCanVote``` -- ordinary full
      reference linkk.
    * ``:cvl:rule:`~../../code/voting/Voting_solution.spec:anyoneCanVote``` --
      relative reference to spec file, the spec file will not be included in the
      displayed text.
    * ``:cvl:invariant:`see this invariant<anInvariant>``` -- a link with explicit title.
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

        For example ``:cvl:invariant:`see this invariant<anInvariant>``` will have
        ``has_explicit_title=True, title="see this invariant", target="anInvariant"``.
        """
        curspec = env.ref_context.get(_curspec_key)

        # Add the current spec to the node's data
        refnode[_curspec_key] = curspec

        # Note the kind (object type)
        kind = self.reftype
        refnode[_kind_key] = kind

        if not has_explicit_title:
            target = target.lstrip("~")  # only has a meaning for the title

        if kind not in {"spec", "property"}:
            # Must have spec name and rule name
            if _spec_separator in target:
                specname, rulename = target.split(_spec_separator, 1)
            else:
                specname = None
                rulename = target
        elif kind == "spec":
            specname = target
            rulename = None
        else:
            # Must be "property"
            specname = None
            rulename = target

        if specname is not None:
            specname = canonical_spec_name_from_filepath(specname, env)

        if not has_explicit_title:
            # if the first character is a tilde, display only the last part of
            # the target, e.g. "~specfile:rulename" -> "rulename"
            if title[0:1] == "~":
                title = rulename

        target = to_refname(self.reftype, specname, rulename)
        return title, target


def pseudo_parse_arglist(
    signode: desc_signature,
    arglist: str,
) -> None:
    """
    "Parse" a list of arguments separated by commas.
    Adapted from sphinx.domains.python._annotations._pseudo_parse_arglist.
    """
    paramlist = addnodes.desc_parameterlist()
    paramlist["multi_line_parameter_list"] = len(arglist) > _max_sig_single_line_len

    try:
        split = arglist.split(",")
        for argument in split:
            argument = argument.strip()
            typename, identifier = argument.split(" ")
            typename = typename.strip()
            identifier = identifier.strip()
            assert re.match(cvl_identifier, identifier)

            paramlist += addnodes.desc_parameter(
                "",  # rawsource
                "",  # text
                addnodes.desc_sig_keyword_type(typename, typename),
                addnodes.desc_sig_space(" ", " "),
                addnodes.desc_sig_name(identifier, identifier),
            )
    except (ValueError, AssertionError):
        # Parsing failed, pass arglist as is
        paramlist = addnodes.desc_parameterlist()
        paramlist += addnodes.desc_parameter(arglist, arglist)

    signode += paramlist


class CVLObject(ObjectDescription[tuple[str, str]]):
    """
    Description of a general CVL object (a directive in the "cvl" domain).
    """

    # If set to ``True`` this object is callable and a `desc_parameterlist` is added
    has_arguments = True

    # Set of object types that are parenthesized
    _parenthesized = {"rule", "invariant", "function", "definition"}

    option_spec: OptionSpec = {
        "noindex": directives.flag,
        "noindexentry": directives.flag,
        "nocontentsentry": directives.flag,
        "spec": directives.unchanged,
        "addspecfiletoname": directives.flag,  # Adding the spec file path to name
        "withoutspecpath": directives.flag,  # Do not add the spec file path as a field
    }

    doc_field_types = [
        Field(
            "title",
            label=_("Title"),
            names=("title",),
            has_arg=False,
        ),
        Field(
            "note",
            label=_("Notice"),
            names=("note", "notice"),
            has_arg=False,
        ),
        Field(
            "status",
            label=_("Verification status"),
            names=("status",),
        ),
        GroupedField(
            "property",
            label=_("Property"),
            names=("property", "properties"),
            can_collapse=False,
            # TODO: add rolename= that will link to a known property
        ),
        # To explain about filtered functions
        GroupedField(
            "filtered",
            label=_("Filtered"),
            names=("filter", "filtered"),
            can_collapse=True,
        ),
        TypedField(
            "parameter",
            label=_("Parameters"),
            names=("param",),
            rolename="param",
            typenames=("paramtype", "type"),
            can_collapse=True,
        ),
        TypedField(
            "return",
            label=_("Returns"),
            names=("return", "returns"),
            rolename="return",
            typenames=("returntype", "type"),
            can_collapse=True,
        ),
    ]

    def get_display_prefix(self) -> list[Node]:
        """
        what is displayed right before the documentation entry
        """
        return [
            addnodes.desc_sig_keyword(self.objtype, self.objtype),
            addnodes.desc_sig_space(),
        ]

    @property
    def _add_spec_file_to_name(self) -> bool:
        """
        Whether to add the spec path as a prefix to the member.
        """
        return self.options.get("addspecfiletoname", False)

    @property
    def _with_spec_path(self) -> bool:
        """
        Whether to add the spec path as a part of the description.
        """
        return not self.options.get("withoutspecpath", False)

    @property
    def _spec_path(self) -> Optional[Path]:
        specname = self.options.get("spec", self.env.ref_context.get(_curspec_key))
        if specname is None:
            return None
        return canonical_spec_link_from_filepath(specname, self.env)

    @property
    def _spec_name(self) -> Optional[str]:
        if self._spec_path is None:
            return None
        return str(self._spec_path)

    def insert_field(self, index: int, fieldname: str, field_content: str):
        """
        Insert a field (e.g. ``:param uint256 amount: the amount transferred``)
        into the content to be parsed.

        :param index: the location in the content to insert the field.
        """
        pass

    def _gen_modname_signode(self, modname: str) -> addnodes.desc_addname:
        """
        Create a node from the spec name (spec file).
        """
        specname = addnodes.desc_addname("", "")
        for part in modname.split("."):
            specname += addnodes.desc_sig_name(part, part)
            specname += addnodes.desc_sig_punctuation(".", ".")
        return specname

    def handle_signature(self, sig: str, signode: desc_signature) -> tuple[str, str]:
        """
        Parse the signature *sig* into individual nodes and append them to
        *signode*. If ValueError is raised, parsing is aborted and the whole
        *sig* is put into a single desc_name node.

        The return value should be a value that identifies the object. It is
        passed to :meth:`add_target_and_index()` unchanged, and otherwise only
        used to skip duplicates.
        """
        sig = sig.strip()
        if "(" in sig and sig[-1:] == ")":
            member, arglist = sig.split("(", 1)
            member = member.strip()
            arglist = arglist[:-1].strip()
        else:
            member = sig
            arglist = None

        specname = self._spec_name
        _, kind = self.name.split(":")
        fullname = to_refname(kind, specname, member)

        signode["module"] = specname
        signode["fullname"] = fullname
        signode["member"] = member

        display_prefix = self.get_display_prefix()
        if len(display_prefix) > 0:
            signode += addnodes.desc_annotation("", "", *display_prefix)

        if specname is not None:
            if self._add_spec_file_to_name:
                # Add spec file name to signature as prefix
                signode += self._gen_modname_signode(specname)

            if self._with_spec_path:
                # Insert the spec name
                # TODO: there must be a better way to do this
                self.content.insert(0, StringList([f":spec: :clink:`{specname}`"]))

        signode += addnodes.desc_name("", "", addnodes.desc_sig_name(member, member))

        if self.has_arguments:
            if arglist is None:
                signode += addnodes.desc_parameterlist()
            else:
                pseudo_parse_arglist(signode, arglist)

        return fullname, member  # TODO: what about hooks? ghosts? ...

    def _object_hierarchy_parts(self, sig_node: desc_signature) -> tuple[str, ...]:
        """
        Returns a tuple of strings, one entry for each part of the object's
        hierarchy (e.g. ``('module', 'submodule', 'Class', 'method')``). The
        returned tuple is used to properly nest children within parents in the
        table of contents, and can also be used within the
        :py:meth:`_toc_entry_name` method.

        This method must not be used outwith table of contents generation.
        """
        if "fullname" not in sig_node:
            return ()
        fullname = sig_node["fullname"]
        return tuple(fullname.split("."))

    def add_target_and_index(
        self, name: tuple[str, str], sig: str, signode: desc_signature
    ) -> None:
        """
        Add cross-reference IDs and entries to self.indexnode, if applicable.

        *name* is whatever :meth:`handle_signature()` returned.
        """
        fullname, _ = name
        node_id = make_id(self.env, self.state.document, "", fullname)
        signode["ids"].append(node_id)
        self.state.document.note_explicit_target(signode)

        domain = cast(CVLDomain, self.env.get_domain(_domain))
        domain.note_object(fullname, self.objtype, node_id, location=signode)

        if self._spec_name is not None:
            # Add spec to the indexed data
            domain.note_spec_obj(self._spec_name, fullname)

        if "noindexentry" not in self.options:
            indextext = self._get_index_text(name)
            if indextext:
                self.indexnode["entries"].append(
                    ("single", indextext, node_id, "", None)
                )

    def _get_index_text(self, name_obj: tuple[str, str]) -> str:
        modname = self._spec_name
        fullname, member = name_obj
        if self.objtype == "spec":
            return _(f"{fullname} (spec)")
        if self.objtype == "methods":
            if modname is None:
                return _(f"{fullname} (methods block)")
            return _(f"{modname} (methods block)")

        if modname is None:
            return _(f"{member} ({self.objtype})")
        return _(f"{member} ({self.objtype} in {modname})")

    def before_content(self) -> None:
        """
        Called before parsing content. Used to set information about the current
        directive context on the build environment.
        Usually used in the context of nested elements.
        """
        pass

    def transform_content(self, contentnode: addnodes.desc_content) -> None:
        """
        Called after creating the content through nested parsing,
        but before the ``object-description-transform`` event is emitted,
        and before the info-fields are transformed.
        Can be used to manipulate the content.
        """
        pass

    def after_content(self) -> None:
        """
        Called after parsing content. Used to reset information about the
        current directive context on the build environment.
        Usually used in the context of nested elements - for de-nesting.
        """
        pass

    def _toc_entry_name(self, sig_node: desc_signature) -> str:
        """
        Returns the text of the table of contents entry for the object.

        This function is called once, in :py:meth:`run`, to set the name for the
        table of contents entry (a special attribute ``_toc_name`` is set on the
        object node, later used in
        ``environment.collectors.toctree.TocTreeCollector.process_doc().build_toc()``
        when the table of contents entries are collected).

        To support table of contents entries for their objects, domains must
        override this method, also respecting the configuration setting
        ``toc_object_entries_show_parents``. Domains must also override
        :py:meth:`_object_hierarchy_parts`, with one (string) entry for each part of the
        object's hierarchy. The result of this method is set on the signature
        node, and can be accessed as ``sig_node['_toc_parts']`` for use within
        this method. The resulting tuple is also used to properly nest children
        within parents in the table of contents.

        An example implementations of this method is within the python domain
        (:meth:`!PyObject._toc_entry_name`). The python domain sets the
        ``_toc_parts`` attribute within the :py:meth:`handle_signature()`
        method.
        """
        # Modified from PyObject domain
        if not sig_node.get("_toc_parts"):
            return ""

        config = self.env.app.config
        objtype = sig_node.parent.get("objtype")
        if config.add_function_parentheses and objtype in self._parenthesized:
            parens = "()"
        else:
            parens = ""
        *parents, name = sig_node["_toc_parts"]
        if config.toc_object_entries_show_parents == "domain":
            return sig_node.get("member", name) + parens
        if config.toc_object_entries_show_parents == "hide":
            return name + parens
        if config.toc_object_entries_show_parents == "all":
            return ".".join(parents + [name + parens])
        return ""


class CVLSpec(SphinxDirective):
    """
    Directive to mark description of a new spec. Adapted from :class:`PyModule`.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: OptionSpec = {
        "noindex": directives.flag,
        "nocontentsentry": directives.flag,
    }

    def run(self) -> list[Node]:
        domain = cast(CVLDomain, self.env.get_domain(_domain))

        modname = self.arguments[0].strip()
        noindex = "noindex" in self.options
        self.env.ref_context[_curspec_key] = modname

        content_node: Element = nodes.section()
        # necessary so that the child nodes get the right source/line set
        content_node.document = self.state.document

        # Add spec name as title
        self.content.insert(
            0, StringList([f"Spec {modname}", "-" * (len(modname) + len("Spec "))])
        )
        nested_parse_with_titles(
            self.state, self.content, content_node, self.content_offset
        )

        ret: list[Node] = []
        if not noindex:
            # Note spec to the domain
            node_id = make_id(self.env, self.state.document, SPECFILE, modname)
            target = nodes.target("", "", ids=[node_id], ismod=True)
            self.set_source_info(target)
            self.state.document.note_explicit_target(target)

            domain.note_object(modname, SPECFILE, node_id, location=target)

            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(target)
            indextext = f"{_(SPECFILE)}; {modname}"
            inode = addnodes.index(entries=[("pair", indextext, node_id, "", None)])
            ret.append(inode)
        ret.extend(content_node.children)
        return ret

    def make_old_id(self, name: str) -> str:
        """Generate old styled node_id.

        Old styled node_id is incompatible with docutils' node_id.
        It can contain dots and hyphens.

        .. note:: Old styled node_id was mainly used until Sphinx-3.0.
        """
        return "spec-%s" % name


class CVLDomain(Domain):
    name = _domain
    label = "CVL"
    kind = "objtype"
    object_types: dict[str, ObjType] = _cvl_object_types

    directives = {
        "rule": CVLObject,
        "invariant": CVLObject,
        "function": CVLObject,
        "definition": CVLObject,
        "hook": CVLObject,
        "ghost": CVLObject,
        "spec": CVLSpec,
        # TODO: property
    }

    roles = {
        "rule": CVLXRefRole(fix_parens=True),
        "invariant": CVLXRefRole(fix_parens=True),
        "function": CVLXRefRole(fix_parens=True),
        "definition": CVLXRefRole(fix_parens=True),
        "hook": CVLXRefRole(),
        "ghost": CVLXRefRole(),
        "spec": CVLXRefRole(),
        # TODO: "methods": CVLObject
    }

    indices = {PropertyIndex, RuleIndex, SpecIndex}

    @property
    def objects(self) -> dict[str, CVLObjectEntry]:
        return self.data.setdefault("objects", {})  # fullname -> object-data

    def note_object(
        self, fullname: str, objtype: str, node_id: str, location: Any = None
    ) -> None:
        """
        Note a CVL object for cross reference, keep it in ``objects`` dictionary.
        """
        if fullname in self.objects:
            # Duplicated
            docname = self.objects[fullname][0]
            logger.warning(
                __("duplicate %s description of %s, other %s in %s"),
                objtype,
                fullname,
                objtype,
                docname,
                location=location,
            )
        self.objects[fullname] = CVLObjectEntry(self.env.docname, node_id, objtype)

        if objtype == "spec":
            spec_entry = self.specs.setdefault(fullname, CVLSpecEntry(True, []))
            spec_entry.has_spec_object = True

    def note_spec_obj(self, spec_refname: str, refname: str):
        spec_entry = self.specs.setdefault(spec_refname, CVLSpecEntry(False, []))
        if refname not in spec_entry.rules_refnames:
            spec_entry.rules_refnames.append(refname)

    @property
    def specs(self) -> dict[str, CVLSpecEntry]:
        """
        We treat each spec file as a different CVL module. The returned dictionary
        has structure: spec-name -> (main spec ref, [spec rules]).
        """
        return self.data.setdefault("specs", {})

    def clear_doc(self, docname: str) -> None:
        # NOTE: copied from the code for the javascript Sphinx domain
        for fullname, (pkg_docname, _node_id, _l) in list(self.objects.items()):
            if pkg_docname == docname:
                del self.objects[fullname]
        for modname, (pkg_docname, _node_id) in list(self.specs.items()):
            if pkg_docname == docname:
                del self.specs[modname]

    def merge_domaindata(self, docnames: list[str], otherdata: dict[str, Any]) -> None:
        """
        Merge in data regarding *docnames* from a different domaindata
        inventory (coming from a subprocess in parallel builds).
        """
        # NOTE: copied from the code for the javascript Sphinx domain
        # XXX check duplicates
        for fullname, (fn, node_id, objtype) in otherdata["objects"].items():
            if fn in docnames:
                self.objects[fullname] = (fn, node_id, objtype)
        for mod_name, (pkg_docname, node_id) in otherdata["specs"].items():
            if pkg_docname in docnames:
                self.specs[mod_name] = (pkg_docname, node_id)

    def find_obj(
        self,
        env: BuildEnvironment,
        name: str,
        spec_name: Optional[str],
        kind: Optional[str],
    ) -> list[tuple[str, CVLObjectEntry]]:
        """
        Find a CVL element for ``name``, using the spec file name
        and the element's ``kind`` (type).
        """
        # skip parenthesis
        if name[-2:] == "()":
            name = name[:-2]

        # Canonicalize spec name
        if spec_name is not None:
            try:
                spec_name = canonical_spec_name_from_filepath(spec_name, env)
            except ValueError:
                spec_name = None  # Unusable

        searches = [name]
        parts = name.split(_spec_separator)
        # Search for "cvl:{kind}:name" and "cvl:{kind}:{spec}:name"
        if parts[0] == _domain:
            parts = parts[1:]

        if parts[0] in self.object_types:
            # Object kind (e.g. rule, property, invariant, ...) exists
            kind = parts[0]
            parts = parts[1:]

        kinds = self.object_types.keys() if kind is None else [kind]
        joined_name = _spec_separator.join(parts)
        for objtype in kinds:
            searches.append(_spec_separator.join((_domain, objtype, joined_name)))
            if spec_name is not None:
                if objtype == "spec":
                    searches.append(to_refname(objtype, spec_name, None))
                else:
                    searches.append(to_refname(objtype, spec_name, joined_name))

        matches = []
        for search_name in searches:
            if search_name in self.objects:
                matches.append((search_name, self.objects.get(search_name)))

        return matches

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """
        Resolve the pending_xref *node* with the given *typ* and *target*.

        This method should return a new node, to replace the xref node,
        containing the *contnode* which is the markup content of the
        cross-reference.

        If no resolution can be found, None can be returned; the xref node will
        then given to the :event:`missing-reference` event, and if that yields no
        resolution, replaced by *contnode*.

        The method can also raise :exc:`sphinx.environment.NoUri` to suppress
        the :event:`missing-reference` event being emitted.
        """
        obj = self.objects.get(target)
        if obj is None:
            return None
        return self._make_refnode(builder, fromdocname, obj, node, contnode, target)

    def _make_refnode(
        self,
        builder: Builder,
        fromdocname: str,
        obj: CVLObjectEntry,
        node: pending_xref,
        contnode: Element,
        name: str,
    ) -> reference:
        if obj.objtype == "spec":
            return make_refnode(
                builder, fromdocname, obj.docname, obj.node_id, contnode, name
            )

        # determine the content of the reference by conditions
        content = find_pending_xref_condition(node, "resolved")
        if content:
            children = content.children
        else:
            # if not found, use contnode
            children = [contnode]

        return make_refnode(
            builder, fromdocname, obj.docname, obj.node_id, children, name
        )

    def resolve_any_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> list[tuple[str, Element]]:
        """
        Resolve the pending_xref *node* with the given *target*.

        The reference comes from an "any" or similar role, which means that we
        don't know the type.  Otherwise, the arguments are the same as for
        :meth:`resolve_xref`.

        The method must return a list (potentially empty) of tuples
        ``('domain:role', newnode)``, where ``'domain:role'`` is the name of a
        role that could have created the same reference, e.g. ``'py:func'``.
        ``newnode`` is what :meth:`resolve_xref` would return.
        """
        spec_name = node.get(_curspec_key)
        kind = node.get(_kind_key)
        matches = self.find_obj(env, target, spec_name, kind)
        if len(matches) == 0:
            return []

        results = []
        for name, obj in matches:
            domain_role = f"{self.name}:{obj.objtype}"
            refnode = self._make_refnode(
                builder, fromdocname, obj, node, contnode, name
            )
            results.append((domain_role, refnode))
        return results

    def get_objects(self) -> Iterable[tuple[str, str, str, str, str, int]]:
        # First yield modules (specs)
        for refname, obj in list(self.objects.items()):
            if obj.objtype == "spec":
                # Use -1 for searches
                yield refname, refname, obj.objtype, obj.docname, obj.node_id, -1
        # Now yield everyone else
        for refname, (docname, node_id, typ) in list(self.objects.items()):
            if typ != "spec":
                _, _, dispname = spec_and_rulename_from_ref(refname, typ)
                yield refname, dispname, typ, docname, node_id, 1

    def get_specname(self, refname: str) -> Optional[str]:
        """
        Returns the canonical spec name of the given object, if exists.
        """
        obj = self.objects.get(refname)
        if obj is None:
            return None
        return spec_and_rulename_from_ref(refname, obj.objtype)[1]

    def get_full_qualified_name(self, node: Element) -> str | None:
        """Return full qualified name for given node."""
        # modname = node.get(_curspec_key)
        # kind = node.get(_kind_key)
        target = node.get("fullname")
        if target is None:
            return None
        else:
            return target


def setup(app: Sphinx) -> dict[str, Any]:
    app.setup_extension("sphinx.directives")
    app.add_domain(CVLDomain)
    return {"parallel_read_safe": False, "parallel_write_safe": False}
