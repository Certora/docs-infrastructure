# Create full pdf
sphinx-build -M latexpdf docs/source/ docs/build/fullpdf \
  -D latex_elements.papersize=a4paper \
  -D latex_logo=_static/logo.png \
  -D latex_toplevel_sectioning=section \
  -D latex_theme=howto \
  -t is_dev_build

# Create pdf of one part
sphinx-build -M latexpdf docs/source/showcase docs/build/partpdf \
  -c docs/source/ \
  -D code_path_override=../../../code \
  -D project="Sphinx showcase" \
  -D html_title="Sphinx showcase" \
  -D latex_elements.papersize=a4paper \
  -D latex_logo=_static/logo.png \
  -D latex_toplevel_sectioning=section \
  -D latex_theme=howto \
  -t is_dev_build

# To create pdfs, run this script from repository root, then:
# cp docs/build/fullpdf/latex/certoradocumentsinfrastructure.pdf docs/source/_static/pdfs/
# cp docs/build/partpdf/latex/sphinxshowcase.pdf docs/source/_static/pdfs/
