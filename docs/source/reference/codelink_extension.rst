.. index::
   single: codelink_extension
   single: extension; codelink_extension
   :name: codelink_extension

Codelink extension
==================
This is a Sphinx extension for linking source code files. The resulting links are either
to local files, or to Github, depending on the configuration.

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
   :lines: 19-22
   :emphasize-lines: 2

Options
^^^^^^^

.. _code_path_variable:

``code_path_override``
   Optional string, determines the :index:`absolute code path`.
   Absolute paths in ``:clink:`` are considered as relative to the *absolute code path*.
   By default, this path is the source directory (e.g. ``docs/source/``).
   This options changes the absolute code path to the one given in ``code_path_override``.
   Note ``code_path_override`` must be relative to the source directory.

``link_to_github``
   Boolean, if true the links will be to the Github remote repository (deduced from
   the repository of the path given in ``:clink:``). Otherwise will link to local files.


Usage
-----

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
