Code blocks
===========

Best practice
-------------

In-place code
-------------

Basic
^^^^^

Code-block
""""""""""

You can insert a *CVL* code block in-place, using the ``code-block`` directive, as
shown below.

.. literalinclude:: cvl_code1.rst
   :language: restructuredtext

*Rendered as:*

.. include:: cvl_code1.rst

Inline CVL
""""""""""
You can add inline *CVL* code using the ``cvl`` role. For example, the following
paragraph:

.. code-block:: restructuredtext

   Type casting between integers in *CVL* has two different forms, :cvl:`assert_uint256`
   and :cvl:`require_uint256`.

*Will be rendered as:*
   
Type casting between integers in *CVL* has two different forms, :cvl:`assert_uint256`
and :cvl:`require_uint256`.



Additional Features
^^^^^^^^^^^^^^^^^^^
Additional features, such as line numbers and emphasized lines are demonstrated below.
You can find more information at: `code-block directive
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block>`_.

.. literalinclude:: cvl_code2.rst
   :language: restructuredtext

*Rendered as:*

.. include:: cvl_code2.rst


.. _code_block_from_external:

From external file
------------------

Use the ``literalinclude`` directive to include code from an external file.
To get the ``/code/`` directory use: ``/../code/``
(providing an absolute path is taken as relative to the ``/source/`` directory).

For example:

.. code-block:: restructuredtext

   .. literalinclude:: /../code/lesson2_started/erc20/Parametric.spec
      :language: cvl
      :lines: 27-52
      :emphasize-lines: 8,9

*Rendered as:*
      
.. literalinclude:: /../code/lesson2_started/erc20/Parametric.spec
  :language: cvl
  :lines: 27-52
  :emphasize-lines: 8,9
