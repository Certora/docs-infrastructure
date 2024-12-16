.. index::
   single: codelink_extension
   single: extension; codelink_extension
   :name: codelink_extension

Codelink extension
==================
This is a Sphinx extension for linking source code files. The resulting links are either
to local files, or to Github, depending on the configuration,
see :ref:`link_to_github_option`. 

The code for this extension is at :mod:`docsinfra.sphinx_utils.codelink_extension`.

Configuration
-------------

Adding the extension
^^^^^^^^^^^^^^^^^^^^^
To use the extension you must add ``docsinfra.sphinx_utils.codelink_extension`` to the 
``extensions`` list in the ``source/conf.py`` file, as shown below. This is done
automatically by the :ref:`certora_doc_quickstart`.

.. literalinclude:: /conf.py
   :language: python
   :start-at: extensions = [
   :end-before: sphinx.ext.graphviz
   :emphasize-lines: 2

.. role:: python(code)
   :language: python

Options
^^^^^^^

.. _link_to_github_option:

``link_to_github``
   Boolean, if true the links will be to the Github remote repository (deduced from
   the repository of the path given in ``:clink:``). Otherwise will link to local files.

.. _code_path_variable:

``code_path_override``
   Optional string, determines the :index:`absolute code path`.
   Absolute paths in ``:clink:`` are considered as relative to the *absolute code path*.
   By default, this path is the source directory (e.g. ``docs/source/``).
   This options changes the absolute code path to the one given in ``code_path_override``.
   Note ``code_path_override`` must be relative to the source directory.

.. _path_remappings_dict:

``path_remappings``
   Optional :python:`dict[str, str]`, where keys are identifiers starting with ``@`` and
   values are paths relative to source directory ((i.e. the directory containing the
   config file). Values which are absolute paths will also be considered as relative to
   the source directory.

   Paths in the ``:clink:`` role using these keys will be resolved using the provided
   values. See :ref:`paths_resolution` for more information.


Usage
-----
See :ref:`paths_resolution` for how paths are resolved.

Syntax
^^^^^^

.. code-block:: restructuredtext

   * :clink:`Optional name <path-to-code>` - in this case "Optional name"
     will be displayed. As noted above, absolute links will be considered as relative
     to the *absolute code path*.
   * :clink:`path-to-code` - in this case the "path-to-code" will be the link's text.

Examples
^^^^^^^^

.. literalinclude:: ../showcase/standard/links_code.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: ../showcase/standard/links_code.rst


Github linking notes
--------------------

* If the *code* folder is not part of a git repository, the extension will fall back
  to local links.
* Determining the link to the correct file depends on Github's current conventions, and
  will likely fail for other hosting services.
* The extension will use the *current active branch* for the link. If the git repository
  is in *detached head* state (common in git sub-modules), it will try to deduce
  the correct branch.
