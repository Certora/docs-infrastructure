Code blocks
===========

Best practice
-------------
It is best to include a code-block from a spec or Solidity file that is part of
a regtest. This will ensure that you will be alerted if there are any breaking changes.
Use the directives described in :ref:`code_block_from_external`.

Using ``includecvl`` (see :ref:`including_cvl_elements` below) has the added benefit that
it is protected against changes to the code file itself. Added or removed lines will
not affect it.


In-place code
-------------

Code-block
^^^^^^^^^^

You can insert a *CVL* code block in-place, using the ``code-block`` directive, as
shown below. The same directive can be used for other languages, such as Solidity.

.. literalinclude:: cvl_code1.rst
   :language: restructuredtext
   :caption: rst

*Rendered as:*

.. include:: cvl_code1.rst


Additional features, such as line numbers and emphasized lines are demonstrated below.
You can find all the options available at: `code-block directive`_.

.. literalinclude:: cvl_code2.rst
   :language: restructuredtext
   :caption: rst

*Rendered as:*

.. include:: cvl_code2.rst


Inline CVL and solidity
^^^^^^^^^^^^^^^^^^^^^^^
You can add inline *CVL* code using the ``:cvl:`` role, and inline Solidity using
the ``:solidity:`` role. For example, the following paragraph:

.. code-block:: restructuredtext

   Type casting between integers in *CVL* has two different forms, :cvl:`assert_uint256`
   and :cvl:`require_uint256`. In the :solidity:`constructor(uin256 x)` ...

.. card::

   Rendered as:
   ^^^^^^^^^^^^
   
   Type casting between integers in *CVL* has two different forms, :cvl:`assert_uint256`
   and :cvl:`require_uint256`. In the :solidity:`constructor(uin256 x)` ...


.. _code_block_from_external:

From external file
------------------

.. _including_cvl_elements:

Including CVL elements
^^^^^^^^^^^^^^^^^^^^^^
Use the ``cvlinclude`` directive to include CVL elements *by name*.
This is the preferred way to include rules, invariants, ghosts and the methods block.
Complete documentation is available at :ref:`includecvl_extension`.

Example
"""""""

.. code-block:: restructuredtext
   
   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: numVoted onlyLegalVotedChanges sumResultsEqualsTotalVotes
      :caption: Voting rules

*Rendered as:*

.. cvlinclude:: /../../code/voting/Voting_solution.spec
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

Including any code
^^^^^^^^^^^^^^^^^^
Use the ``literalinclude`` directive to include code from an external file.
As above, providing an absolute path is taken as relative to the ``/source/`` directory.
For all possible options of ``literalinclude``, see the `literalinclude directive`_.

.. important::

   An alternative to using line numbers when including code are the
   ``:start-after:``, ``:start-at:``, ``:end-before:``, and ``:end-at:`` options.
   These accept string, which they match to find the desired lines.

For example:

.. code-block:: restructuredtext

   .. literalinclude:: /../../code/voting/Voting.sol
      :language: solidity
      :lines: 4-
      :emphasize-lines: 4-6

*Rendered as:*
      
.. literalinclude:: /../../code/voting/Voting.sol
   :language: solidity
   :lines: 4-
   :emphasize-lines: 4-6


.. Links
   -----

.. _literalinclude directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude

.. _code-block directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
