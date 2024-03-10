Indexing and glossary
=====================

.. _howto_indexing:

Indexing
--------
To add terms to the :ref:`genindex`, place an appropriate ``index`` directive before
the part you wish to index. See `Sphinx - index directive`_ for a comprehensive
description of this directive, here are some simple examples.

Simple indexing
^^^^^^^^^^^^^^^
The following will create three index entries.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. todo:: Test this one!

      .. code-block:: markdown

         ```{index} municipality, town, city
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext

         .. index:: municipality, town, city

Adding single values
^^^^^^^^^^^^^^^^^^^^

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown

         ```{eval-rst}
         .. index::
            single: propositional logic
            single: logic; propositional
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext

         .. index::
            single: propositional logic
            single: logic; propositional

This will create two index entries, the first as "propositional logic" and the second
will be a sub-index under "logic".

Adding reference labels to indexes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use the ``:name:`` option for adding a label that can be used with ``:ref:``. For example:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown

         ```{eval-rst}
         .. index::
            :name: intro_to_formal
         ```

         ## Introduction to formal verification

         See {ref}`intro_to_formal` ...

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext

         .. index::
            :name: intro_to_formal
      
         Introduction to formal verification
         -----------------------------------
            
         See :ref:`intro_to_formal` ...

Inline indexing
^^^^^^^^^^^^^^^
You can add index entries inline. Here is an example from
`Sphinx - index directive`_:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey
      
      .. code-block:: markdown
         
         This is a normal MyST {index}`paragraph` that contains several
         {index}`index entries <pair: index; entry>`.

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         This is a normal reST :index:`paragraph` that contains several
         :index:`index entries <pair: index; entry>`.


.. _howto_glossary:

Glossary
--------
For complete documentation on the ``glossary`` directive see `Sphinx - Glossary`_.

Creating a glossary
^^^^^^^^^^^^^^^^^^^
Create a glossary using the ``glossary`` directive, followed by a
:ref:`howto_definition_list` of the desired terms. A term can have several names, as
shown in the following example.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: glossary_example.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: glossary_example.rst
         :language: restructuredtext

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: glossary_example.rst

Referencing a glossary term
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use the ``term`` role to refer to a glossary term, for example:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         * Simple reference such as {term}`CVL`
         * Showing alternative text like {term}`The Prover <Prover>`

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         * Simple reference such as :term:`CVL`
         * Showing alternative text like :term:`The Prover <Prover>`

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   * Simple reference such as :term:`CVL`
   * Showing alternative text like :term:`The Prover<Prover>`


.. Links
   -----

.. _Sphinx - index directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-index

.. _Sphinx - Glossary:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#glossary
