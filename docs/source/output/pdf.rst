.. index::
   single: pdf
   single: output; pdf
   :name: generating_pdf

Generating PDF output
=====================

.. important::

   To generate pdf output you will need a LaTex installation with the ``pdflatex``
   engine.

.. note::

   Although it is possible to build `Sphinx`_ documents directly into pdf, here we only
   describe building it via LaTex first, since the output is better.


Basic use
---------
Running the command below will:

#. create a LaTex file inside ``<output-dir>/latex``
#. run ``pdflatex`` on the LaTex file twice (to get correct references)


.. code-block:: bash

   sphinx-build -M latexpdf <source-dir> <output-dir>


Options
-------
To modify the resulting LaTex document, one can add various options to the
configuration file ``conf.py``. These options are detailed in
`Options for LaTex output`_, and also in `LaTex Customiztion`_.

Another way to control the options is modifying them in the ``sphinx-build`` command
using the ``-D`` option. See `sphinx-build`_ for more details.

Example
^^^^^^^
Adding the following lines to ``conf.py`` will change the paper size and add a logo.

.. code-block:: python

   latex_elements["papersize"] = "a4paper"
   latex_logo = "_static/logo.png"  # Relative to the source dir, must be png

Alternatively, the following command will do the same:

.. code-block:: bash

   sphinx-build -M latexpdf docs/source docs/build/ -D latex_elements.papersize=a4paper \
     -D latex_logo=_static/logo.png

Important options
^^^^^^^^^^^^^^^^^

* ``latex_elements.papersize``: ``a4paper`` or ``letterpaper``
* ``latex_elements.pointsize``: ``10pt``, ``11pt`` or ``12pt``
* ``latex_logo``: path to logo ``.png`` file, relative to source dir
* ``latex_toplevel_sectioning``: ``part``, ``chapter`` or ``section``
* ``latex_theme``: ``manual`` (larger document) or ``howto`` (smaller document)


Preferred format
----------------
Use the following options to create a smaller document with the Certora logo.

.. code-block:: bash

   sphinx-build -M latexpdf docs/source/ docs/build/ \
     -D latex_elements.papersize=a4paper \
     -D latex_logo=_static/logo.png \
     -D latex_toplevel_sectioning=section \
     -D latex_theme=howto


Building partial document
-------------------------
If you wish to create a pdf of only a part of the documentation, you need only
modify the source dir, and update the ``code_path`` option to be relative to the new
source. For example, to create a pdf only from the :ref:`sphinx_showcase`:

.. code-block:: bash
   
   sphinx-build -M latexpdf docs/source/showcase docs/build/ \
     -D latex_elements.papersize=a4paper \
     -D latex_logo=_static/logo.png \
     -D latex_toplevel_sectioning=section \
     -D latex_theme=howto \
     -D code_path=/../../../code


.. Links:
   ------

.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html

.. _Options for LaTex output:
   https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

.. _LaTex Customiztion: https://www.sphinx-doc.org/en/master/latex.html

.. _sphinx-build: https://www.sphinx-doc.org/en/master/man/sphinx-build.html
