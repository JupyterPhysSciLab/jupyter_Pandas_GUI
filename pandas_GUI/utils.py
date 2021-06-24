######
# Jupyter JS call utilities
######
def new_cell_immediately_below():
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(
        JS('Jupyter.notebook.focus_cell();' \
           'Jupyter.notebook.insert_cell_below();'))
    pass


def select_cell_immediately_below():
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(JS('Jupyter.notebook.select_next(true);'))


def move_cursor_in_current_cell(delta):
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(
        JS('var curPos = Jupyter.notebook.get_selected_cell().code_' \
           'mirror.doc.getCursor();' \
           'var curline = curPos.line; var curch = curPos.ch +' + str(
            delta) + ';' \
                     'Jupyter.notebook.get_selected_cell().code_mirror.' \
                     'doc.setCursor({line:curline,ch:curch});'))
    pass


def insert_text_into_next_cell(text):
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(JS('Jupyter.notebook.select_next(true);' \
               'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'replaceSelection("' + text + '");'))
    pass


def insert_text_at_beginning_of_current_cell(text):
    # append \n to line insert as a separate line.
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(
        JS('Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'setCursor({line:0,ch:0});' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'replaceSelection("' + text + '");'))
    pass


def insert_newline_at_end_of_current_cell(text):
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(
        JS('var lastline = Jupyter.notebook.get_selected_cell().' \
           'code_mirror.doc.lineCount();' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'setCursor(lastline,0);' \
           'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
           'replaceSelection("\\n' + text + '");'))
    pass

def select_containing_cell(elemID):
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    # Create a synthetic click in the cell to force selection of the cell
    # containing the table
    display(JS(
    'var event = new MouseEvent("click", {' \
    'view: window,' \
    'bubbles: true,' \
    'cancelable: true' \
    '});' \
    'var start = new Date().getTime();' \
    'var elem = document.getElementById("'+elemID+'");' \
    'do {' \
    'elem = document.getElementById("'+elemID+'");' \
    '} while ((elem == null) && (new Date().getTime() < start+5000));' \
    'if (elem == null){' \
    'alert("It took more than 5 seconds to build element.");}' \
    'var cancelled = !elem.dispatchEvent(event);' \
    'if (cancelled) {' \
    # A handler called preventDefault.
    'alert("Something is wrong. Try running the cell that creates this GUI' \
           '.");' \
    '}'))
    pass

def delete_selected_cell():
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(JS('Jupyter.notebook.delete_cell(' \
               'Jupyter.notebook.get_selected_index());'))
    pass

def find_pandas_dataframe_names():
    """
    This operation will search the interactive name space for pandas
    DataFrame objects. It will not find DataFrames that are children
    of objects in the interactive namespace. You will need to provide
    your own operation for finding those.
    :return: List of string names for objects in the global interactive
    namespace that are pandas DataFrames.
    """
    from pandas import DataFrame as df
    from IPython import get_ipython

    dataframenames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
            dataframenames.append(k)
    return dataframenames

def find_figure_names():
    from plotly.graph_objects import Figure, FigureWidget
    from IPython import get_ipython

    fignames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k],
                                                       (Figure,FigureWidget)):
            fignames.append(k)
    return fignames
