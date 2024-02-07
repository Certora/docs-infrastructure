.. Certora Documents Infrastructure documentation master file, created by
   sphinx-quickstart on Tue Jan 30 12:57:03 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Certora Documents Infrastructure's documentation!
============================================================

.. rubric:: A package for easily creating `Sphinx`_ docs for `Certora`_.


Features
--------

Include CVL code
^^^^^^^^^^^^^^^^
Easily include CVL code from spec files.

.. code-block:: restructuredtext
   :caption: source

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: onlyLegalVotedChanges sumResultsEqualsTotalVotes numVoted
      :spacing: 1

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. cvlinclude:: /../../code/voting/Voting_solution.spec
      :cvlobject: onlyLegalVotedChanges sumResultsEqualsTotalVotes numVoted
      :spacing: 1

Link to Github
^^^^^^^^^^^^^^

.. code-block:: restructuredtext
   :caption: source

   See for example :clink:`Voting solution spec </voting/Voting_solution.spec>`.

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   See for example :clink:`Voting solution spec </voting/Voting_solution.spec>`.

CVL syntax highlighting
^^^^^^^^^^^^^^^^^^^^^^^

.. cvlinclude:: /../../code/voting/Voting_solution.spec
   :cvlobject: methods

Create pdf versions
^^^^^^^^^^^^^^^^^^^
For example
:download:`Certora documents infrastructure </_static/pdfs/certoradocumentsinfrastructure.pdf>`.


Contents
--------

.. toctree::
   :maxdepth: 2
   :numbered: 2

   quickstart/index
   output/pdf
   showcase/index
   reference/index

.. The following is a trick to get the general index on the side bar.

.. toctree::
   :hidden:

   genindex


.. todo:: Add information about the ``myst-parser`` package.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. Links
   -----

.. _Sphinx: https://www.sphinx-doc.org/
.. _Certora: https://www.certora.com/
