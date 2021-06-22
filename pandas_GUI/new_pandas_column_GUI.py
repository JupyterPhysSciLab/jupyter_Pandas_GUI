def new_pandas_column_GUI(dfs_info=None, show_text_col = False):
    """
    If passed no parameters this will look for all the dataframes in the user
    namespace and make them available for adding a new column to. Once a
    dataframe is chosen only the numerical columns from that dataframe will
    be available for inclusion in the new column expression.

    If you wish to allow only certain dataframes or have them show up as
    user friendly names in the menus provide that information in the first
    paramater dfs_info.

    To allow inclusion of text columns pass True for show_text_col.

    :param show_text_col: bool (default = False). When True columns containing
    text will be shown.
    :param dfs_info: List of Lists of strings [[globalname, userfriendly]
    ],..]
        :globalname: string name of the object in the user global name space.
        :userfriendly: string name to display for user selection.
    :return:
    """

    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Dropdown, Label, Text, Button, Checkbox
    from IPython.display import display, HTML
    from IPython import get_ipython
    from .utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell
    # will be set to true if needed for operations used that require numpy.
    if dfs_info == None:
        from .utils import find_pandas_dataframe_names
        dfs_info = []
        for k in find_pandas_dataframe_names():
            dfs_info.append([k,k])
    friendly_to_globalname = {k[1]:k[0] for k in dfs_info}

    #### Define GUI Elements ####

    # DataFrame Choice
    tempopts = []
    tempopts.append('Choose')
    for k in dfs_info:
        tempopts.append(k[1])
    whichframe = Dropdown(options=tempopts,
                                description='DataFrame: ',)

    def update_columns(change):
        dfname = friendly_to_globalname[change['new']]
        user_ns = get_ipython().user_ns
        tempcols = user_ns[dfname].columns.values
        tempopt = ['Choose column to insert.']
        for k in tempcols:
            if show_text_col:
                tempopt.append(k)
            else:
                if user_ns[dfname][k].dtype != 'O':
                    tempopt.append(k)
        whichcolumn.options = tempopt
        pass

    whichframe.observe(update_columns, names='value')
    # Step 1
    newname = Text(placeholder='Type name for new column.')
    step1instr = Label(
        value='Pick a name for the new column. The expression will be ' \
              'built in the cell below. Click the "Insert" button when ' \
              'you are satisfied with the name.')
    insertname = Button(description="Insert")

    def do_insertname(change):
        framename = friendly_to_globalname[whichframe.value]
        text = framename + '[\'' + newname.value + '\'] = '
        insert_text_into_next_cell(text)
        pass

    insertname.on_click(do_insertname)

    step1 = VBox([step1instr, HBox([newname,
                                           insertname])])
    # Step 2
    whichcolumn = Dropdown(options=['Choose column to insert.'],
                           description='Column: ',
                           )

    def column_insert(change):
        col = change['new']
        if col == 'Choose column to insert.':
            return
        framename = friendly_to_globalname[whichframe.value]
        text = framename + '[\'' + col + '\']'
        insert_text_into_next_cell(text)
        whichcolumn.value = 'Choose column to insert.'
        pass

    whichcolumn.observe(column_insert, names='value')
    step2instr = Label(
        value='Choose columns and operations from the menus to insert ' \
              'into your expression. Your choices will replace selected ' \
              'text or insert at the current cursor position.')
    oplst = ['Choose an operation to insert.', '+', '-', '*', '/', '**',
             'exp()', 'log()', 'ln()', 'sqrt()', 'sin()', 'cos()',
             'tan()', 'cot()', 'asin()', 'acos()', 'atan()', 'acot()']
    whichop = Dropdown(options=oplst,
                       description='Operation: ')
    def op_insert(change):
        need_numpy = False
        np_list = ['exp()', 'log()', 'ln()', 'sqrt()', 'sin()', 'cos()',
                   'tan()', 'cot()', 'asin()', 'acos()', 'atan()',
                   'acot()']
        op = change['new']
        if op == 'Choose an operation to insert.':
            return
        if op in np_list:
            need_numpy = True
            op = 'np.' + op
        else:
            op = ' ' + op + ' '
        insert_text_into_next_cell(op)
        if need_numpy:
            move_cursor_in_current_cell(-1)
        whichop.value = 'Choose an operation to insert.'
        pass

    whichop.observe(op_insert, names='value')

    step2drops = HBox([whichcolumn, whichop])
    step2 = VBox([step2instr, step2drops])
    # Step 3
    step3instr1 = Label(
        value='Carefully check the expression for typos before selecting' \
              ' "Do it!".')
    step3instr2 = Label(
        value=' * Parentheses, brackets or braces highlighted in red ' \
              'are missing their partner.')
    step3instr3 = Label(
        value=' * Check that all double and single quotes are also ' \
              'properly paired.')
    step3instr4 = Label(
        value=' * Check that all function calls are prefaced by ' \
              'an \'np.\'.')
    show_updated_df_box = Checkbox(description='Display updated '
                                                 'dataset.',
                                   value=True)
    gen_col_but = Button(description='Do it!')

    def run_new_col_decl(change):
        from IPython.display import display, HTML
        from IPython.display import Javascript as JS
        select_cell_immediately_below()
        # import numpy if numpy functions used (they could have put in by hand -- insert by default?)
        text = 'import numpy as np # Necessary for function calls\\n'
        insert_text_at_beginning_of_current_cell(text)
        # if show updated dataframe is checked append dataframe name as last line.
        if show_updated_df_box.value == True:
            text = friendly_to_globalname[whichframe.value]
            insert_newline_at_end_of_current_cell(text)
        # run composed operation
        display(JS('Jupyter.notebook.get_selected_cell().execute()'))
        # TODO: add deletion of composer cell after this is a functioning module.
        pass

    gen_col_but.on_click(run_new_col_decl)
    step3instr = VBox([step3instr1, step3instr2, step3instr3,
                        step3instr4])
    step3act = VBox([show_updated_df_box, gen_col_but])
    step3 = HBox([step3instr, step3act])

    steps = Tab([step1, step2, step3])
    steps.set_title(0, 'Step 1')
    steps.set_title(1, 'Step 2')
    steps.set_title(2, 'Step 3')

    display(HTML(
        "<h3 style='text-align:center;'>Pandas New Calculated Column Composer</h3>"))
    pdComposer = VBox([whichframe, steps])
    display(pdComposer)
    new_cell_immediately_below()
    pass


def tstGUI():
    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Dropdown, Label, Text, Button, Checkbox
    from IPython.display import display, HTML
    from IPython import get_ipython
    from pandas import DataFrame as df
    def tstobs(change):
        global_dict = get_ipython().user_ns
        print(global_dict[change['new']].columns)
        pass

    global_dict = get_ipython().user_ns
    dataframes = []
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
            dataframes.append(k)
    tstdrp = Dropdown(options = dataframes)
    tstdrp.observe(tstobs,names='value')
    display(tstdrp)
    pass