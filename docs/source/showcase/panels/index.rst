Panels
======

The panels use the
`sphinx-design <https://sphinx-design.readthedocs.io/en/rtd-theme/index.html>`_ extension.
Follow the link for more details.

Single card
-----------

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: panels_single_panel_example.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: panels_single_panel_example.rst
         :language: restructuredtext

*Rendered as:*

.. include:: panels_single_panel_example.rst

Grid with two cards
-------------------

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: panels_two_cards_grid.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: panels_two_cards_grid.rst
         :language: restructuredtext

*Rendered as:*

.. include:: panels_two_cards_grid.rst


Placing code side by side
^^^^^^^^^^^^^^^^^^^^^^^^^

*Note the limited width of the columns!*

.. grid:: 2

    .. grid-item-card::  Spec

       .. code-block:: cvl
          :caption: Invariant

          invariant totalIsBiggest(address user)
              balanceOf(user) <= totalBalance();

    .. grid-item-card::  Solidity

       .. code-block:: solidity
          :caption: Solidity

          function balanceOf(
            address user
          ) external view returns (bool) {
            return _balances[user];
          }

Drop-down
---------

Drop-down content is useful for providing hidden hints. Here is a simple drop-down:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. literalinclude:: panels_dropdown.md
         :language: markdown

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. literalinclude:: panels_dropdown.rst
         :language: restructuredtext

*Rendered as:*

.. include:: panels_dropdown.rst
