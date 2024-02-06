.. Miscellaneous Sphinx capabilities

Miscellaneous
=============

.. index:: table

Tables
------
There are several ways to add tables in reStructuredText, there are described in

- `reStructuredText Primer - Tables`_
- `CSV Tables`_
- `List Tables`_

Here is an example of a *list table*.

.. code-block:: restructuredtext

   .. list-table:: Table title
      :header-rows: 1
   
      * - Column Header
        - 2nd Column Header
        - 3rd Column Header
   
      * - Row 1 Column 1 item
        - Row 1 Column 2 item
        - An item
   
      * - An item
        - Row 2 Column 2 item
        - Row 2 Column 3 item

*Rendered as:*

.. list-table:: Table title
   :header-rows: 1

   * - Column Header
     - 2nd Column Header
     - 3rd Column Header

   * - Row 1 Column 1 item
     - Row 1 Column 2 item
     - An item

   * - An item
     - Row 2 Column 2 item
     - Row 2 Column 3 item


.. _reStructuredText Primer - Tables:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#tables

.. _CSV Tables: https://docutils.sourceforge.io/docs/ref/rst/directives.html#csv-table

.. _List Tables: https://docutils.sourceforge.io/docs/ref/rst/directives.html#list-table


.. index::
   single: image
   single: picture

Adding an image
---------------
To insert an image or picture use the ``.. image`` directive, as shown below.
The specified path to the image ``images/symbolic_pool_diagram.png`` is relative to
the file containing the directive.

.. literalinclude:: image.rst
   :language: restructuredtext

*Rendered as:*

.. include:: image.rst

Notes
^^^^^
The image path
    A relative path should be relative to the ``.rst`` file. An absolute path is
    treated as relative to the top ``source/`` directory. See `Sphinx Image Directive`_
    for more on this.

Additional options
    Options, such as alternative text for missing images and scaling, are described in
    `Docutils Image Directive`_.


.. _Sphinx Image Directive:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#images

.. _Docutils Image Directive:
   https://docutils.sourceforge.io/docs/ref/rst/directives.html#image


.. index::
   single: video

Adding a video clip
-------------------
To add a video clip file we use the `sphinxcontrib-video`_ extension.
Note that the preferred folder to place the video file is the ``source/_static/`` folder.
For example:

.. literalinclude:: video.rst
   :language: restructuredtext

*Rendered as:*

.. include:: video.rst

.. seealso:: See `sphinxcontrib-video Quickstart`_ for additional options.

.. index::
   single: closed captions
   single: subtitles

Combining closed captions
^^^^^^^^^^^^^^^^^^^^^^^^^
You cannot use a separate file for the closed captions (subtitles). Instead you must
embed the closed captions inside the video itself.

Here is one recipe to include a closed captions file in your video.
Suppose you have an mp4 video ``InvariantsClip.mp4``  and a closed captions file
named ``InvariantsClip.srt``, you can combine them using the `FFmpeg`_ package with the
following command:

.. code-block:: bash

   ffmpeg -i InvariantsClip.mp4 -vf subtitles=InvariantsClip.srt InvariantsClip_subtitles.mp4


.. _sphinxcontrib-video: https://sphinxcontrib-video.readthedocs.io/en/latest/index.html

.. _sphinxcontrib-video Quickstart:
   https://sphinxcontrib-video.readthedocs.io/en/latest/quickstart.html

.. _FFmpeg: https://ffmpeg.org/
