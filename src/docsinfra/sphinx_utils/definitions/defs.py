"""
Certora specific definitions for :mod:`sphinx`.
"""


class CertoraSphinxTags:
    """
    Tags are a way to conditionally include content in the tutorials, using the ``only``
    directive. See `including content based on tags
    <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#including-content-based-on-tags>`_.
    See also in Sphinx documentation `conf tags
    <https://www.sphinx-doc.org/en/master/usage/configuration.html#conf-tags>`_.
    """

    @property
    def is_dev_build(self) -> str:
        """
        This tag indicates that the current Sphinx build is a *dev build*,
        hence development notes will be included.
        """
        return "is_dev_build"


TAGS = CertoraSphinxTags()
