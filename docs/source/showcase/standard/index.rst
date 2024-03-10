Standard markup
===============

Basic inline markup
-------------------

Fonts
^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: basic.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: basic.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: basic.rst

Headings
^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: restructuredtext
         :caption: Headings conventions

         # Top level

         ## Second level

         ### Third level

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      For a full list and explanation, see: `reStructuredText Sections`_.
      Note there are no levels assigned to particular heading characters. Sphinx 
      deduces the levels in each ``.rst`` file.
      
      .. code-block:: restructuredtext
         :caption: Headings conventions
      
         Section heading
         ===============
      
         Sub-section
         -----------
      
         Sub sub-section
         ^^^^^^^^^^^^^^^
      
         Even lower level
         """"""""""""""""

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

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists.rst

Numbered lists
^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: lists_numbered.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: lists_numbered.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists_numbered.rst

.. _howto_definition_list:

Definition list
^^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: lists_definitions.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: lists_definitions.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: lists_definitions.rst

Links
-----

External links
^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: links_external.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: links_external.rst
         :language: restructuredtext

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

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: youtube_example.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: youtube_example.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: youtube_example.rst

----

Internal links
^^^^^^^^^^^^^^

Link anywhere inside the documentation.


.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      See `MyST Cross-referencing`_.

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         .. _my-reference-label:
         
         Cross-reference inside documentation
         """"""""""""""""""""""""""""""""""""
         
         Set up a label ``.. _my-reference-label`` as shown above. 
         Note underscore prefix in the label name.
         
         To reference use the ``:ref:`` directive like so: :ref:`my-reference-label`.

----

.. _link_to_code_file:

Link to code file on Github
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Link to a code file using the ``:clink:`` role.
The link will be either to `GitHub`_ or to local file, depending on the value
of ``link_to_github`` variable in the :file:`source/conf.py` file.

Absolute paths will be considered as relative to the *absolute code path*
-- see :ref:`code_path_variable`. For complete documentation, see
:ref:`codelink_extension`.

The basic syntax is:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
         :caption: Syntax
      
         {clink}`Optional name <relative-path-to-code-file>`
         {clink}`Optional name <absolute path relative to absolute code path>`

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
         :caption: Syntax
      
         :clink:`Optional name <relative-path-to-code-file>`
         :clink:`Optional name <absolute path relative to absolute code path>`

For example:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: links_code.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: links_code.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: links_code.rst


.. Links
   -----

.. _reStructuredText Sections:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections

.. _MyST Cross-referencing:
   https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html

.. _GitHub: https://github.com/
