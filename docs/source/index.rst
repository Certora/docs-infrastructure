.. Certora Documents Infrastructure documentation master file, created by
   sphinx-quickstart on Tue Jan 30 12:57:03 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Certora Documents Infrastructure's documentation!
============================================================

.. rubric:: Easily create `Sphinx`_ docs for `Certora`_.


Features
--------

CVL domain
^^^^^^^^^^

.. cvl:spec:: @voting/Voting_solution.spec

   An example of describing a spec file.

.. cvl:rule:: myRule(uint256 amount, address from)
   :spec: @voting/Voting_solution.spec

   :title: My special rule
   :status: Verified
   :param amount: The amount
   :param from: the one from which
   :property: someprop

   Free text.

   We can also reference other rules, e.g. :cvl:invariant:`anInvariant`.
   Similarly full name as :cvl:rule:`@voting/Voting_solution.spec:anyoneCanVote`.
   Similarly :cvl:rule:`~../../code/voting/Voting_solution.spec:anyoneCanVote`.
   Or even :cvl:invariant:`see this invariant<anInvariant>`.

----

.. cvl:invariant:: anInvariant(address user)

   :title: some invariant
   :status: Violated
   :param user: The user

----

.. cvl:rule:: anyoneCanVote(address voter, bool isInFavor)
   :spec: /voting/Voting_solution.spec

   :title: Anyone can vote once
   :status: Verified

Include CVL code
^^^^^^^^^^^^^^^^
Easily include CVL code from spec files.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: features/includecvl.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: features/includecvl.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: features/includecvl.rst


Link to Github
^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: features/githublink.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: features/githublink.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: features/githublink.rst

CVL syntax highlighting
^^^^^^^^^^^^^^^^^^^^^^^

.. cvlinclude:: /voting/Voting_solution.spec
   :cvlobject: methods

Create pdf versions
^^^^^^^^^^^^^^^^^^^
For example
:download:`Certora documents infrastructure </_static/pdfs/certoradocumentsinfrastructure.pdf>`.

----

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
   cvl-ruleindex
   cvl-specindex
   cvl-propertyindex


Indices and tables
==================

* :ref:`genindex`
* :ref:`cvl-ruleindex`
* :ref:`cvl-specindex`
* :ref:`cvl-propertyindex`
* :ref:`search`


.. Links
   -----

.. _Sphinx: https://www.sphinx-doc.org/
.. _sphinx-quickstart: https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html
.. _Certora: https://www.certora.com/
.. _MyST: https://myst-parser.readthedocs.io/
