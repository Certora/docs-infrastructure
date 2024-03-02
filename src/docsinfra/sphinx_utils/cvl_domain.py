"""
Defines a CVL domain for Sphinx. A Domain is meant to be a group of "object" description
directives for objects of a similar nature, and corresponding roles to create references
to them.
"""
from pathlib import Path
from typing import Any, Iterable, NamedTuple, Optional, Union, cast

from docutils import nodes
from docutils.nodes import Element, Node, reference, system_message
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.addnodes import desc_signature, pending_xref
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, Index, IndexEntry, ObjType
from sphinx.domains.python import _pseudo_parse_arglist  # TODO: replace this!
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

logger = logging.getLogger(__name__)

_domain = "cvl"
MODULE = "module"
_module = f"{_domain}:{MODULE}"


class CVLObjectEntry(NamedTuple):
    docname: str  # The document where it is to be found.
    node_id: str  # The anchor name for the object.
    objtype: str  # Object type, a key in ``CVLDomain.object_types``, aka ``kind``


class CVLModuleEntry(NamedTuple):
    """
    Each spec file as a different module.
    """

    docname: str
    node_id: str


class CVLXRefRole(XRefRole):
    """
    Roles for cross-referencing cvl domain directives.
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
        # Copy the module
        refnode[_module] = env.ref_context.get(_module)

        if not has_explicit_title:
            target = target.lstrip("~")  # only has a meaning for the title

            # if the first character is a tilde, display only the last part of
            # the target, e.g. "~specfile.rulename" -> "rulename"
            if title[0:1] == "~":
                title = title[1:]
                dot = title.rfind(".")
                if dot != -1:
                    title = title[dot + 1 :]  # noqa

        return title, target


def module_name_from_filepath(
    filepath: Optional[Union[str, Path]], env: BuildEnvironment
) -> Optional[str]:
    """
    Provides a shorter name for a module (i.e. spec file).
    Returns the name of the spec file, without the ".spec" extension and using
    "." instead of "/". Also makes it relative to the "code/" folder, if possible.

    :param filepath: a path to the spec file
    """
    if filepath is None:
        return None

    path = Path(filepath)

    # Use path relative to code path if provided
    code_conf = CodeLinkConfig(env)
    if code_conf.is_codepath_overridden:
        try:
            path = code_conf.get_rel_path(path)
        except ValueError:
            # Not relative to code path, ignore
            pass

    parts = path.parts
    if parts[0] == "/":
        parts = parts[1:]  # Ignore it
    name = ".".join(parts)
    if path.suffix == ".spec":
        name = name[: -len(".spec")]
    return name


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
        "module": directives.unchanged,  # TODO: change to spec?
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
        # To explain about filtered functions
        Field(
            "filtered",
            label=_("Filtered"),
            names=("filter", "filtered"),
            has_arg=False,
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
        Whether to add the module path as a prefix to the member.
        """
        return self.options.get("addspecfiletoname", False)

    @property
    def _with_spec_path(self) -> bool:
        """
        Whether to add the module path as a part of the description.
        """
        return not self.options.get("withoutspecpath", False)

    @property
    def _module_name(self) -> Optional[str]:
        modname = self.options.get("module", self.env.ref_context.get(_module))
        return module_name_from_filepath(modname, self.env)

    def insert_field(self, index: int, fieldname: str, field_content: str):
        """
        Insert a field (e.g. ``:param uint256 amount: the amount transferred``)
        into the content to be parsed.

        :param index: the location in the content to insert the field.
        """
        pass

    def _gen_modname_signode(self, modname: str) -> addnodes.desc_addname:
        """
        Create a node from the module name (spec file).
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

        # NOTE: self.objtype contains the cvl kind (e.g. "rule", "invariant", ...).
        # There is no need to add it to the full name, since member names should be
        # unique.
        fullname = f"{member}"
        modname = self._module_name
        if modname is not None:
            fullname = f"{modname}.{fullname}"

        signode["module"] = modname
        signode["fullname"] = fullname
        signode["member"] = member

        display_prefix = self.get_display_prefix()
        if len(display_prefix) > 0:
            signode += addnodes.desc_annotation("", "", *display_prefix)

        if modname is not None:
            if self._add_spec_file_to_name:
                # Add spec file name to signature as prefix
                signode += self._gen_modname_signode(modname)

            if self._with_spec_path:
                # Insert the module name
                # TODO: there must be a better way to do this
                self.content.insert(0, StringList([f":spec: {modname}"]))

        signode += addnodes.desc_name("", "", addnodes.desc_sig_name(member, member))

        if self.has_arguments:
            if arglist is None:
                signode += addnodes.desc_parameterlist()
            else:
                _pseudo_parse_arglist(signode, arglist)

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

        if "noindexentry" not in self.options:
            indextext = self._get_index_text(name)
            if indextext:
                self.indexnode["entries"].append(
                    ("single", indextext, node_id, "", None)
                )

    def _get_index_text(self, name_obj: tuple[str, str]) -> str:
        modname = self._module_name
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


class CVLModule(SphinxDirective):
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
        self.env.ref_context[_module] = modname

        content_node: Element = nodes.section()
        # necessary so that the child nodes get the right source/line set
        content_node.document = self.state.document

        # Add module name as title
        self.content.insert(
            0, StringList([f"Spec {modname}", "-" * (len(modname) + len("Spec "))])
        )
        nested_parse_with_titles(
            self.state, self.content, content_node, self.content_offset
        )

        ret: list[Node] = []
        if not noindex:
            # note module to the domain
            node_id = make_id(self.env, self.state.document, MODULE, modname)
            target = nodes.target("", "", ids=[node_id], ismod=True)
            self.set_source_info(target)
            self.state.document.note_explicit_target(target)

            domain.note_module(modname, node_id)
            domain.note_object(modname, MODULE, node_id, location=target)

            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(target)
            indextext = f"{_(MODULE)}; {modname}"
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
        return "module-%s" % name


class CVLDomain(Domain):
    name = _domain
    label = "CVL"
    kind = "objtype"
    object_types: dict[str, ObjType] = {
        "rule": ObjType(_("rule"), "rule"),
        "invariant": ObjType(_("invariant"), "invariant"),
        "function": ObjType(_("function"), "function"),
        "definition": ObjType(_("definition"), "definition"),
        "hook": ObjType(_("hook"), "hook"),
        "ghost": ObjType(_("ghost"), "ghost"),
        "methods": ObjType(_("methods"), "methods"),
        "spec": ObjType(_("spec"), "spec"),  # Spec file
    }

    directives = {
        "rule": CVLObject,
        "invariant": CVLObject,
        "function": CVLObject,
        "definition": CVLObject,
        "hook": CVLObject,
        "ghost": CVLObject,
        "spec": CVLModule,
        # TODO: "methods": CVLObject, "ghost" and "hook"?
    }

    roles = {
        "rule": CVLXRefRole(fix_parens=True),
        "invariant": CVLXRefRole(fix_parens=True),
        "function": CVLXRefRole(fix_parens=True),
        "definition": CVLXRefRole(fix_parens=True),
        "hook": CVLXRefRole(),
        "ghost": CVLXRefRole(),
        # TODO: "methods": CVLObject, and "ghost"
    }

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

    @property
    def modules(self) -> dict[str, CVLModuleEntry]:
        """
        We treat each spec file as a different CVL module.
        """
        return self.data.setdefault("modules", {})  # modname -> docname, node_id

    def note_module(self, modname: str, node_id: str) -> None:
        """
        Note a CVL module for cross-reference,
        We treat each spec file as a different CVL module.
        """
        self.modules[modname] = CVLModuleEntry(self.env.docname, node_id)

    def clear_doc(self, docname: str) -> None:
        # NOTE: copied from the code for the javascript Sphinx domain
        for fullname, (pkg_docname, _node_id, _l) in list(self.objects.items()):
            if pkg_docname == docname:
                del self.objects[fullname]
        for modname, (pkg_docname, _node_id) in list(self.modules.items()):
            if pkg_docname == docname:
                del self.modules[modname]

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
        for mod_name, (pkg_docname, node_id) in otherdata["modules"].items():
            if pkg_docname in docnames:
                self.modules[mod_name] = (pkg_docname, node_id)

    def find_obj(
        self,
        env: BuildEnvironment,
        name: str,
        mod_name: Optional[str],
        kind: Optional[str],
    ) -> list[tuple[str, CVLObjectEntry]]:
        """
        Find a CVL element for ``name``, using the module (spec file) name
        and the element's ``kind`` (type).
        """
        # skip parenthesis
        if name[-2:] == "()":
            name = name[:-2]

        searches = []
        if mod_name is not None and len(mod_name) > 0:
            if kind is not None and len(kind) > 0:
                searches.append(".".join([mod_name, kind, name]))
            else:
                searches.append(".".join([mod_name, name]))
        else:
            if kind is not None and len(kind) > 0:
                searches.append(".".join([kind, name]))
        searches.append(name)

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
        mod_name = node.get(f"{self.name}:module")
        kind = node.get(f"{self.name}:{self.kind}")
        matches = self.find_obj(env, target, mod_name, kind)
        if len(matches) == 0:
            return None
        if len(matches) > 1:
            logger.warning(
                __("more than one target found for cross-reference %r: %s"),
                target,
                ", ".join(match[0] for match in matches),
                type="ref",
                subtype=self.label,
                location=node,
            )

        # Choose the first match
        name, obj = matches[0]
        return self._make_refnode(builder, fromdocname, obj, node, contnode, name)

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
        mod_name = node.get(f"{self.name}:module")
        kind = node.get(f"{self.name}:{self.kind}")
        matches = self.find_obj(env, target, mod_name, kind)
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
            if obj.objtype != "spec":
                yield refname, refname, obj.objtype, obj.docname, obj.node_id, 1

    def get_full_qualified_name(self, node: Element) -> str | None:
        """Return full qualified name for given node."""
        modname = node.get(f"{self.name}:module")
        kind = node.get(f"{self.name}:{self.kind}")
        target = node.get("reftarget")
        if target is None:
            return None
        else:
            return ".".join(filter(None, [modname, kind, target]))


def setup(app: Sphinx) -> dict[str, Any]:
    app.setup_extension("sphinx.directives")
    app.add_domain(CVLDomain)
    return {"parallel_read_safe": False, "parallel_write_safe": False}
