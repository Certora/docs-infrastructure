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

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         ```{only} is_dev_build
      
         The following will only be included in dev builds.
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
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

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         ```{todo}
         This is an example of a TODO comment, it can also have several paragraphs.
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         .. todo:: This is an example of a TODO comment, it can also have several paragraphs.

.. card::

   Rendered as:
   ^^^^^^^^^^^^

   .. todo:: This is an example of a TODO comment, it can also have several paragraphs.


To create a list containing all the TODO comments:


.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         ```{todolist}
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         .. todolist::
