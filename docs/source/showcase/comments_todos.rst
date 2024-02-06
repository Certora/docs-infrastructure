Comments and TODOs
==================

RestructuredText comments
-------------------------

.. code-block:: restructuredtext

   .. This is a comment in RestructuredText, the entire paragraph will be ignored
      by sphinx. Just note the indentation.


.. index:: dev-build
   :name: dev_build

Development build
-----------------
We can have content that is visible only in *dev-build* mode.
To enable dev-build mode, add ``-t is_dev_build`` to the ``sphinx-build`` command
(see :ref:`build_html` and :ref:`generating_pdf`). For example:

.. code-block:: bash

   sphinx-build -b html docs/source/ docs/build/html -t is_dev_build

.. note::

   In dev-build the html title (on the side bar) will have "- Development" added to it.
   This behavior can be modified in the ``/source/conf.py`` file.


Contents for dev-build only
^^^^^^^^^^^^^^^^^^^^^^^^^^^
To produce contents that will appear only in dev-build, use the ``.. only`` directive,
like this:

.. code-block:: restructuredtext
   :caption: rst

   .. only:: is_dev_build

      The following will only be included in dev builds.

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. only:: is_dev_build

      The following will only be included in dev builds.


.. index:: todo

TODOs
^^^^^
*TODO* comments will only appear in dev-build. To add a TODO comment:

.. code-block:: restructuredtext
   :caption: rst

   .. todo:: This is an example of a TODO comment, it can also have several paragraphs.

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. todo:: This is an example of a TODO comment, it can also have several paragraphs.


To create a list containing all the TODO comments:

.. code-block:: restructuredtext

   .. todolist::
