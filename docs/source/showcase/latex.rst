Using Latex
===========

In-line math
------------
For inline math use the ``:math:`` role. For example:

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         Let {math}`\mathcal{C}` be the category of groups and {math}`f: G \to H` be a
         morphism in {math}`\mathcal{C}`.

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         Let :math:`\mathcal{C}` be the category of groups and :math:`f: G \to H` be a
         morphism in :math:`\mathcal{C}`.

*Rendered as:*

Let :math:`\mathcal{C}` be the category of groups and :math:`f: G \to H` be a
morphism in :math:`\mathcal{C}`.

.. _centered_latex_math_section:

Centered math
-------------
Use the ``math`` directive, as shown below. See `Directives - math
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-math>`_
for additional options and examples.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
      
         ```{math}
         (a + b)^2  &=  (a + b)(a + b) \\
                    &=  a^2 + 2ab + b^2
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
      
         .. math::
      
            (a + b)^2  &=  (a + b)(a + b) \\
                       &=  a^2 + 2ab + b^2

*Rendered as:*

.. math::

   (a + b)^2  &=  (a + b)(a + b) \\
              &=  a^2 + 2ab + b^2


Advanced use
------------
Here is an example of showing a conditional function.

.. tab-set::

   .. tab-item:: MyST (.md)
      :sync: mystKey

      .. code-block:: markdown
         :caption: Conditional function in Latex
      
         ```{math}
         :nowrap:

         \begin{equation}
         f(x) =
         \begin{cases}
              0  & \text{if } x \leq 0 \\
              x^2 & \text{otherwise}
         \end{cases}
         \end{equation}
         ```

   .. tab-item:: reStructuredText (.rst)
      :sync: rstKey

      .. code-block:: restructuredtext
         :caption: Conditional function in Latex
      
         .. math::
            :nowrap:
      
            \begin{equation}
            f(x) =
            \begin{cases}
                 0  & \text{if } x \leq 0 \\
                 x^2 & \text{otherwise}
            \end{cases}
            \end{equation}

*Rendered as:*

.. math::
   :nowrap:

   \begin{equation}
   f(x) =
   \begin{cases}
        0  & \text{if } x \leq 0 \\
        x^2 & \text{otherwise}
   \end{cases}
   \end{equation}

.. note::

   When using the ``.. math::`` directive, Sphinx will wrap the latex code inside the
   Latex ``split`` environment before rendering it. Using the ``:nowrap:`` option
   disables this behavior.

   For example, the code from :ref:`centered_latex_math_section` is rendered as the
   following Latex code:

   .. code-block:: latex
   
      \begin{split}
          (a + b)^2  &=  (a + b)(a + b) \\
                     &=  a^2 + 2ab + b^2
      \end{split}


