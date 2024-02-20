.. index::
   single: includecvl
   single: extension; includecvl
   :name: includecvl_extension

Include CVL extension
=====================
This Sphinx extension for including CVL elements from spec files in the document.
It is able to include invariants, rules and ghosts by name.
The code for this extension is at :mod:`docsinfra.sphinx_utils.cvlinclude`.

.. important::

   This extension uses the CVLDoc package.

Configuration
-------------

Adding the extension
^^^^^^^^^^^^^^^^^^^^^
To use the extension you must add ``docsinfra.sphinx_utils.cvlinclud`` to the 
``extensions`` list in the ``sourc/conf.py`` configuration file, as shown below.
This is done automatically by the :ref:`certora_doc_quickstart`.

.. literalinclude:: /conf.py
   :language: python
   :start-at: extensions = [
   :end-before: sphinx.ext.graphviz
   :emphasize-lines: 3


Usage
-----

Syntax
^^^^^^

.. code-block:: restructuredtext

   .. cvlinclude:: <spec-file-path>
      :cvlobject: <element-id> [<element-id> ...]
      :spacing: 2

``spec-file-path``
   Path to spec file. If relative should be relative to the current file.
   If absolute, it will be considered as relative to the ``/source/`` directory.

``:cvlobject:``
   Ids of elements to include, separated by spaces.
   See :ref:`cvl_element_id_syntax` for forming elements ids.
   Currently accepts rules, invariants, ghosts, hooks and the methods block.
   To include the methods block, add ``methods`` to this list.
   These elements will appear in the order they are given, and will include their
   documentation in addition to their source code.

``:spacing:``
   The number of lines between two elements, defaults to one.

In addition, this extension support all the options of the `literalinclude directive`_,
such as ``:caption:`` and ``:emphasize-lines:``.

.. important::

   If omitting the ``:cvlobject:`` option, you must add the ``:language: cvl`` option,
   since the extension will not assume this code is CVL.


.. _cvl_element_id_syntax:

CVL element id syntax
^^^^^^^^^^^^^^^^^^^^^
* For elements with unique name, one can simply use their name. These are
  :cvl:`definition`, :cvl:`function`, :cvl:`ghost`, :cvl:`invariant` and :cvl:`rule`.
* For the methods block, use ``methods``.
* For hooks:

  #. For opcode hook: ``HookOpcode:<opcode>`` where ``<opcode>`` is the *opcode* used.
  #. For load hook use: ``HookSload:<slot_pattern>``.
  #. For store hook use: ``HookSstore:<slot_pattern>``.

.. note::
   In general you can always use ``<kind>:<name-or-data>`` where:

   #. ``kind`` is one of |SUPPORTED_KINDS|.
   #. ``name-or-data`` is either

      * the element's name -- for elements with unique name, or
      * the opcode or slot-pattern, as appropriate.


Simple Example
^^^^^^^^^^^^^^

.. code-block:: restructuredtext

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: methods onlyLegalVotedChanges
      :spacing: 2
      :caption: Voting rules
      :emphasize-lines: 2

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: methods onlyLegalVotedChanges
      :spacing: 2
      :caption: Voting rules
      :emphasize-lines: 2


Hook example
^^^^^^^^^^^^

.. code-block:: restructuredtext

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: someoneVoted HookSstore:_hasVoted[KEY address voter]
      :spacing: 1
      :caption: Hook example

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: someoneVoted HookSstore:_hasVoted[KEY address voter]
      :spacing: 1
      :caption: Hook example


.. Links
   -----

.. _literalinclude directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude
