[General](#general-notes) | [Make Docs](#constructing-the-documentation)
## General Notes

## Constructing the Documentation

1. Make sure pdoc is installed and updated in the virtual environment `pip 
   install -U pdoc`.
2. The main README is used as the first page of the documentation. However, 
   the location requires some of the links to the images to be changed. So 
   a copy of the file needs to be made and edited (will automate if this 
   becomes standard).
    * Make a copy of README.md from the root level into the docs directory.
    * In the copy for each relative reference `src = "docs/DataSets/..."` 
      add `..
      /` so that 
      they read `src = "DataSets/..."`.
3. Make edits to the file `Pandas_GUI_Doc_Home.html`.
4. At the root level run pdoc `pdoc --logo Pandas_GUI_Icon.svg -html -o 
   docs pandas_GUI`
5. Edit the created `index.html` so that the refresh points to 
   `Pandas_GUI_Doc_Home.html`.
