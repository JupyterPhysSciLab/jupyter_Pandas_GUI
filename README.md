**jupyter_new_Pandas_column_GUI**

GUI to help the user construct expressions for new calculated Pandas
columns. This GUI is meant to run in an interactive Jupyter notebook.
It is based on Jupyter widgets.

**Current Features:**

* Dropdown to choose the DataFrame to work with.
* 

**Wishlist:**

**Installation**

Installation using pip into a virtual environment is recommended.

_Production_

1. If not installed, install pipenv:`$ pip3 install --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to Python](https://docs.python-guide.org/dev/virtualenvs/).
1. Navigate to the directory where this package will be installed.
1. Start a shell in the environment `$ pipenv shell`.
1. Install using pip.
    1. `$ pip install jupyter_new_Pandas_column_GUI`. This will install 
       Jupyter into the same virtual
    environment if you do not already have it on your machine. If Jupyter is already
    installed the virtual environment will use the existing installation. This takes
    a long time on a Raspberry Pi. It will not run on a 3B+ without at least 1 GB of
    swap. See: [Build Jupyter on a Pi](https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian).
    1. Still within the environment shell test this by starting jupyter
`$ jupyter notebook`. Jupyter should launch in your browser.
        1. Open a new notebook using the default (Python 3) kernel.
        1. In the first cell import the input_table module:
            `from new_pandas_column_GUI import *`
        1. To try use the command `???(df_info)` in the next cell. This should 
           generate a blank code cell
        and another code cell that has a table in the output for you to define your table dimensions.
        1. If you define the dimensions the input table will be created for you.
        
1. _Optional_ You can make this environment available to an alternate Jupyter install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment `$ pipenv shell` in the directory for  virtual
    environment will do that.
    1. Issue the command to add this as a kernel to your personal space: 
    `$ python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    1. More information is available in the Jupyter/Ipython documentation. A simple tutorial from Nikolai Jankiev
    (_Parametric Thoughts_) can be found [here](https://janakiev.com/til/jupyter-virtual-envs/). 
    
_Development_

Simply replace `$ pip install jupyter_new_Pandas_column_GUI` with `$ pip 
install -e ../jupyter_new_Pandas_column_GUI` in the _Production_
instructions.

**Issues or comments**

[JupyterPhysSciLab/jupyter_new_Pandas_column_GUI](https://github.com/JupyterPhysSciLab/jupyter_new_Pandas_column_GUI)