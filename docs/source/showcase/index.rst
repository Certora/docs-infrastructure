.. Sphinx showcase and short guide.

.. _sphinx_showcase:

****************************
Sphinx tutorial and showcase
****************************

This chapter describes the most useful Sphinx directives and roles. There are examples
for both markdown and reStructuredText files.

* If you're using *markdown* files (:file:`.md`), these use the `MyST`_ package, and the
  MyST examples are what you need.
* Those using *reStructuredText* files (:file:`.rst`) should refer to the reStructuredText
  examples.

For additional information see:

* `reStructuredText Primer`_
* `Sphinx Directives`_
* `MyST`_


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   standard/index
   code_blocks/index
   indexing_glossary
   comments_todos
   admonitions/index
   panels/index
   latex
   misc


.. todo::

   Missing topics to add:

   * table ot contents (mainly the ``hidden`` option)
   * adding images and using the ``only-light`` and ``only-dark`` classes in furo
   * tabs (from sphinx-design)
   * footnotes
   * ``.. rubric``,  ``.. centered`` and ``.. hlist``


.. Links
   -----

.. _reStructuredText Primer:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

.. _Sphinx Directives:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html

.. _MyST: https://myst-parser.readthedocs.io/
