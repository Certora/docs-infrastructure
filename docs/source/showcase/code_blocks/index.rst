Code blocks
===========

Best practice
-------------
It is best to include a code-block from a spec or Solidity file that is part of
a regtest. This will ensure that you will be alerted if there are any breaking changes.
Use the directives described in :ref:`code_block_from_external`.

Including source code for CVL elements using the ``includecvl`` directive
(see :ref:`including_cvl_elements` below) has the added benefit that it is protected
against changes to the code file itself. Added or removed lines will not affect it.


In-place code
-------------

Code-block
^^^^^^^^^^

You can insert a *CVL* code block in-place, using the ``code-block`` directive, as
shown below. The same directive can be used for other languages, such as Solidity.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: cvl_code1.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: cvl_code1.rst
         :language: restructuredtext

*Rendered as:*

.. include:: cvl_code1.rst

Additional features, such as line numbers and emphasized lines are demonstrated below.
You can find all the options available at: `code-block directive`_.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: cvl_code2.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: cvl_code2.rst
         :language: restructuredtext

*Rendered as:*

.. include:: cvl_code2.rst


Inline CVL and solidity
^^^^^^^^^^^^^^^^^^^^^^^
.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      You can add inline *CVL* code using the ``:cvl:`` role, and inline Solidity using
      the ``:solidity:`` role. To do so you must first define these roles at the top
      of your :file:`.md` file, like so:
      
      .. code-block:: markdown

         ```{role} cvl(code)
         :language: cvl
         ```
 
         ```{role} solidity(code)
         :language: solidity
         ```

      Now we can use them, as in the following example:

      .. code-block:: markdown

         Type casting between integers in *CVL* has two different forms,
         {cvl}`assert_uint256` and {cvl}`require_uint256`.
         In the {solidity}`constructor(uin256 x)` ...

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      You can add inline *CVL* code using the ``:cvl:`` role, and inline Solidity using
      the ``:solidity:`` role. These roles are defined in the :file:`conf.py` file.
      For example, the following paragraph:

      .. code-block:: restructuredtext

         Type casting between integers in *CVL* has two different forms,
         :cvl:`assert_uint256` and :cvl:`require_uint256`. In the
         :solidity:`constructor(uin256 x)` ...

.. card::

   Rendered as:
   ^^^^^^^^^^^^
   
   Type casting between integers in *CVL* has two different forms, :cvl:`assert_uint256`
   and :cvl:`require_uint256`. In the :solidity:`constructor(uin256 x)` ...


.. _code_block_from_external:

From external file
------------------

Use the ``cvlinclude`` directive to include code snippets from files.

Syntax
^^^^^^

.. code-block:: restructuredtext

   .. cvlinclude:: path-to-file, see below
      :language: language (optional), see below
      :cvlobject: cvl objects to show, available only for spec files, see below
      :spacing: <spacing-number>
      :caption: caption (optional), see below
      :lines: line-numbers of the snippet (optional)
      :start-at: optional string marking the first line of included code
      :start-after: optional string, the first line of the code starts after
      :end-at: optional string marking the last line of included code
      :end-before: optional string, the last line of the included code is before this

path-to-file
   The path to the file containing the code snippet. The path is resolved according
   to the same :ref:`paths_resolution` used for the ``:clink:`` role.

language
   This is not needed for paths with suffixes ``.spec``, ``.sol`` or ``.conf``.
   For these the appropriate language (i.e. CVL, Solidity and Json) will be used by
   default.
   See :attr:`~docsinfra.sphinx_utils.includecvl.CVLInclude.file_suffix_to_language`.

cvlobject
   See :ref:`including_cvl_elements` below.

spacing-number
   The number of lines between two CVL elements. Applicable only to spec files and
   directives using the ``:cvlobject:`` option. Defaults to one.

caption
   If an empty caption is provided, the directive will use the default caption,
   which is a code link to the file displaying the file's name, i.e.:

   .. code-block:: restructuredtext

      :clink:`file-name <path-to-file>`

Note
""""
In addition ``cvlinclude`` supports all options supported by ``literalinclude``,
see `literalinclude directive`_.


.. _including_cvl_elements:

Including CVL elements
^^^^^^^^^^^^^^^^^^^^^^
Use the ``cvlinclude`` directive to include CVL elements *by name*.
This is the preferred way to include rules, invariants, ghosts and the methods block.
Complete documentation is available at :ref:`includecvl_extension`.

Example
"""""""

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown

         ```{cvlinclude} ../../../../code/voting/Voting_solution.spec
         :cvlobject: numVoted onlyLegalVotedChanges sumResultsEqualsTotalVotes
         :caption: Voting rules

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
         
         .. cvlinclude:: ../../../../code/voting/Voting_solution.spec
            :cvlobject: numVoted onlyLegalVotedChanges sumResultsEqualsTotalVotes
            :caption: Voting rules

*Rendered as:*

.. cvlinclude:: ../../../../code/voting/Voting_solution.spec
   :cvlobject: numVoted onlyLegalVotedChanges sumResultsEqualsTotalVotes
   :caption: Voting rules

* If the path to the spec file is absolute, it is considered as relative to the
  ``/source/`` directory.
* The ``:cvlobject:`` option accepts names of CVL elements (rule, invariant and ghosts).
  To include the :cvl:`methods` block, add ``methods`` to these names.
  The elements will be shown in the order they are given.

.. note::

   Hooks are not supported (since they are not supported by the ``CVLDoc`` package).
   Use ``literalinclude`` below.

Other Examples
^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown

         ```{cvlinclude} @voting/Voting.sol
         :lines: 4-
         :emphasize-lines: 5-7
         :caption:
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext

         .. cvlinclude:: @voting/Voting.sol
            :lines: 4-
            :emphasize-lines: 5-7
            :caption:

*Rendered as:*
      
.. cvlinclude:: @voting/Voting.sol
   :lines: 4-
   :emphasize-lines: 5-7
   :caption:


.. Links
   -----

.. _literalinclude directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude

.. _code-block directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
