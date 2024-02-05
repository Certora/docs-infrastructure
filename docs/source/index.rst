.. Certora Documents Infrastructure documentation master file, created by
   sphinx-quickstart on Tue Jan 30 12:57:03 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Certora Documents Infrastructure's documentation!
============================================================

.. toctree::
   :maxdepth: 2
   :numbered: 2
   :caption: Contents:

   quickstart/index
   output/pdf
   showcase/index
   reference/index


Example of including CVL elements
---------------------------------

.. cvlinclude:: /../../code/voting/Voting_solution.spec
   :cvlobject: onlyLegalVotedChanges sumResultsEqualsTotalVotes numVoted
   :spacing: 3

Limitations
"""""""""""
* Currently there is no way to include hooks


Example of linking
------------------
See for example :clink:`Voting solution spec <voting/Voting_solution.spec>`.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
