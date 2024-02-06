Configuration
=============

The configuration is determined by the ``/source/conf.py`` file.
See `Sphinx - Configuration` for a full list of configurable properties.

In addition, various extensions and themes have their own configurations possible,
for example:

* The `Furo theme`_
* The spelling extension `sphinxcontrib.spelling`_

Main configurable options
-------------------------

``project``
   The project's name, also the title of the html and pdf documents.

``html_title``
   Optional title to use in the side-bar, defaults to ``project``.

``exclude_patterns``
   A list of paths and patterns to ignore. This helps reduce warnings regarding paths
   under the ``/source/`` folder that are not part of the document tree.

``rst_prolog``
   A string of reStructuredText that will be included at the beginning of every source
   read. This is useful for adding default roles.


.. Links
   ----

.. _Sphinx - Configuration: https://www.sphinx-doc.org/en/master/usage/configuration.html

.. _Furo theme: https://pradyunsg.me/furo/

.. _sphinxcontrib.spelling: https://sphinxcontrib-spelling.readthedocs.io/
