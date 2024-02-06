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

``code_path``
   A string, the path to the *code folder* relative to the source directory. 
   If empty the source directory will be used. This will be the base path for
   code links.

``link_to_github``
   Boolean, if true the links will be to the Github remote repository (deduced from
   the repository of the ``code_path``). Otherwise will link to local files.


Usage
-----

Syntax
^^^^^^

.. code-block:: restructuredtext

   * :clink:`Optional name <path relative to code_path>` - in this case "Optional name"
     will be displayed
   * :clink:`path-relative-to-code_path` - in this case the "path-relative-to-code_path"
     will be the link's text

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
