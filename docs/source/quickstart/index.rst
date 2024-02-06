.. index::
   single: quickstart

Quickstart
==========


Installation
------------
#. Clone the `docsinfra repository`_
#. Install the Python package by running the following from the cloned repository's
   folder:

   .. code-block:: bash

         pip3 install -e .

.. warning::

   It is always recommended to use a Python virtual environment, such as `venv`_,
   when installing a Python package.


Initialization
--------------
Use the ``certora-doc-quickstart`` script to quickly initialize a document. 

.. code-block:: bash

   certora-doc-quickstart <PROJECT_DIR> --project <PROJECT_NAME>

This will create two folders inside ``PROJECT_DIR``:

#. ``source`` - for source files (i.e. `reStructuredText`_)
#. ``build`` - for the resulting html (or latex) files

See :ref:`certora_doc_quickstart` for more information.

.. _build_html:

Build html
----------
To build html run:

.. code-block:: bash

   sphinx-build -b html <path to source> <path to build>/html

View the resulting web pages in ``<path to build>/html/index.html`` on your web browser.

To build a pdf, see :ref:`generating_pdf`.


Example
-------
Suppose there is a project folder at ``root``, with spec files under ``root/code``, as
shown below.

.. code-block:: text
   :caption: Project initial folder structure

   root (top project dir)
     └── code
          └── ... spec and conf files

To quickly start a document with project name "Certora project", and
documentation and build files under ``root/docs``, run the following command
from ``root``:

.. code-block:: bash

   certora-doc-quickstart docs -p "Certora project" --code ../../code

.. note::

   The reason we give the code path as ``../../code`` is that it needs to be
   relative to ``root/docs/source/`` folder.

.. code-block:: text
   :caption: Project folder structure after quickstart

   root
     ├── docs
     │    ├── source
     │    │    ├── index.rst (root documentation file)
     │    │    └── conf.py (configuration file)
     │    └── build
     │         └── html (created by sphinx-build command)
     │              └── index.html (root html file)
     └── code
          └── ... spec and conf files

Build the html file by running from ``root``:

.. code-block:: bash

   sphinx-build -b html docs/source/ docs/build/html

View ``root/docs/build/html/html.index`` on your browser.


.. Links:
   ------

.. _docsinfra repository: https://github.com/shoham-certora/docs-infrastructure

.. _venv: https://docs.python.org/3.10/library/venv.html

.. _reStructuredText:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
