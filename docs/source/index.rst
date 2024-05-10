.. Certora Documents Infrastructure documentation master file, created by
   sphinx-quickstart on Tue Jan 30 12:57:03 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Certora Documents Infrastructure's documentation!
============================================================

.. rubric:: Easily create `Sphinx`_ docs for `Certora`_.


Features
--------

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

.. cvlinclude:: /../../code/voting/Voting_solution.spec
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
   example.rst

.. The following is a trick to get the general index on the side bar.

.. toctree::
   :hidden:

   genindex


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. Links
   -----

.. _Sphinx: https://www.sphinx-doc.org/
.. _sphinx-quickstart: https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html
.. _Certora: https://www.certora.com/
.. _MyST: https://myst-parser.readthedocs.io/
