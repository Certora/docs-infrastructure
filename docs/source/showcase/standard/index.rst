Standard markup
===============

Basic inline markup
-------------------

Fonts
^^^^^
   
.. literalinclude:: basic.rst
   :language: restructuredtext
   :caption: rst


.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: basic.rst

Headings
^^^^^^^^
See `reStructuredText Primer - Sections
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections>`_.

Horizontal rule
^^^^^^^^^^^^^^^
Use four dashes ``----`` (with empty lines above and below) to get a horizontal rule like
the one below.

----


Lists
-----

Bullet lists
^^^^^^^^^^^^

.. literalinclude:: lists.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists.rst

Numbered lists
^^^^^^^^^^^^^^

.. literalinclude:: lists_numbered.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists_numbered.rst

Definition lists
^^^^^^^^^^^^^^^^

.. literalinclude:: lists_definitions.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists_definitions.rst

Links
-----

External links
^^^^^^^^^^^^^^

.. literalinclude:: links_external.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: links_external.rst

----

.. index::
   single: video; youtube
   single: youtube

Embedding a Youtube video
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: youtube_example.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: youtube_example.rst

----

Internal links
^^^^^^^^^^^^^^

Link anywhere inside the documentation.

.. code-block:: restructuredtext
   :caption: rst

   .. _my-reference-label:
   
   Cross-reference inside documentation
   """"""""""""""""""""""""""""""""""""
   
   Set up a label ``.. _my-reference-label`` as shown above.
   Note underscore prefix in the label name .
   To reference use the ``:ref:`` directive like so:  :ref:`my-reference-label`.

*Rendered as:*

.. _my-reference-label:

Cross-reference inside documentation
""""""""""""""""""""""""""""""""""""

Set up a label ``.. _my-reference-label`` as shown above.
Note underscore prefix in the label name .
To reference use the ``:ref:`` directive like so:  :ref:`my-reference-label`.

.. note::

   This example was taken from
   `Cross-referencing arbitrary locations
   <https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#ref-role>`_.

----

.. _link_to_code_file:

Link to code file
^^^^^^^^^^^^^^^^^

Refer to a code file in the ``code`` folder using the ``:clink:`` role.
The ``code`` folder is defined by the ``code_path`` variable in the ``source/conf.py``
file.

.. code-block:: restructuredtext
   :caption: Syntax

   :clink:`Optional name <relative-path-from-code-dir>`

For example:

.. literalinclude:: links_code.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: links_code.rst


.. important::

   Whether the links are to Github or to local files is determined by the
   ``link_to_github`` variable in the ``source/conf.py`` file.
