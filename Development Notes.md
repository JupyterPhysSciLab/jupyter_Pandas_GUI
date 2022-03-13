[General](#general-notes) | [Make Docs](#constructing-the-documentation)
## General Notes
1. Have not completely converted to JPSLUtils for javascript tools and 
   accessing code cells. This will need to be complete before trying to 
   make the software JLab vs ClassicNB aware.

## Constructing the Documentation

1. Make sure pdoc is installed and updated in the virtual environment `pip 
   install -U pdoc`.
2. The main README is used as the first page of the documentation. However, 
   the location requires some of the links to the images to be changed. So 
   a copy of the file needs to be made and edited (will automate if this 
   becomes standard).
    * Copy of README.md from the root level to `docs/intro.md`.
    * In the copy for each relative reference `src = "docs/DataSets/..."` 
      remove `docs/` so that they read `src = "DataSets/..."`.
3. Make edits to the file `Pandas_GUI_Doc_Home.html`.
4. At the root level run pdoc `pdoc --logo Pandas_GUI_Icon.svg --logo-link 
https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/ --footer-text 
   "jupyter_Pandas_GUI vX.X.X" -html -o docs pandas_GUI` where `X.X.X` is the 
   version number.
5. Edit the created `index.html` so that the refresh points to 
   `Pandas_GUI_Doc_Home.html`.

## Tasks for Documentation
* Version number in docs footer