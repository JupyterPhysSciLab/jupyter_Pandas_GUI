name = "pandas_GUI"
"""
This code utilizes Jupyter widgets to provide a python expression composer GUI
to generate code to add a new column to an existing Pandas DataFrame.
"""

import os

# locate directory for this package.
# absolute path to directory containing this file.
mydir = os.path.dirname(__file__)

# load any supporting files

from pandas_GUI.new_pandas_column_GUI import new_pandas_column_GUI