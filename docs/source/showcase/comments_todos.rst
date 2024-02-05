Comments and TODOs
==================

RestructuredText comments
-------------------------

.. code-block:: restructuredtext

   .. This is a comment in RestructuredText, the entire paragraph will be ignored
      by sphinx. Just note the indentation.


Contents for dev-build only
---------------------------
To produce contents that will appear only in dev builds, use the ``.. only`` directive,
like this:

.. code-block:: restructuredtext

   .. only:: is_dev_build

      The following will only be included in dev builds.

*Rendered as:*

.. only:: is_dev_build

   The following will only be included in dev builds.


TODOs
-----
A TODO comment will only appear in a dev build. It will appear both in-place and in
the global :ref:`the_todo_list`. To add a TODO comment:

.. code-block:: restructuredtext

   .. todo:: This is an example of a TODO comment, it can also have several paragraphs.

*Rendered as:*

.. todo:: This is an example of a TODO comment, it can also have several paragraphs.
