Indexing and glossary
=====================

.. _howto_indexing:

Indexing
--------
To add terms to the :ref:`genindex`, place an appropriate ``.. index`` directive before
the part you wish to index. See `Sphinx - index directive`_ for a comprehensive
description of this directive, here are some simple examples.

Simple indexing
^^^^^^^^^^^^^^^
The following will create three index entries.

.. code-block:: restructuredtext

   .. index:: municipality, town, city

Adding single values
^^^^^^^^^^^^^^^^^^^^

.. code-block:: restructuredtext

   .. index::
      single: propositional logic
      single: logic; propositional

This will create two index entries, the first as "propositional logic" and the second
will be a sub-index under "logic".

Adding reference labels to indexes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use the ``:name:`` option for adding a label that can be used with ``:ref:``. For example:

.. code-block:: restructuredtext

   .. index:: formal
      :name: intro_to_formal

      Introduction to formal verification
      -----------------------------------
      
      See :ref:`intro_to_formal` ...

Inline indexing
^^^^^^^^^^^^^^^
You can add index entries inline. Here is an example from
`Sphinx - index directive`_:

.. code-block:: restructuredtext

   This is a normal reST :index:`paragraph` that contains several
   :index:`index entries <pair: index; entry>`.


.. _howto_glossary:

Glossary
--------
For complete documentation on the ``glossary`` directive see `Sphinx - Glossary`_.

Creating a glossary
^^^^^^^^^^^^^^^^^^^
Create a glossary using the ``.. glossary::`` directive, followed by a
:ref:`howto_definition_list` of the desired terms. A term can have several names, as
shown in the following example.

.. literalinclude:: glossary_example.rst
   :language: restructuredtext
   :caption: rst

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. include:: glossary_example.rst

Referencing a glossary term
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use the ``:term:`` role to refer to a glossary term, for example:

.. code-block:: restructuredtext
   :caption: rst

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
