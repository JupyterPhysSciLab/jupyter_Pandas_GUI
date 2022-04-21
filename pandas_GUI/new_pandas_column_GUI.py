def new_pandas_column_GUI(df_info=None, show_text_col = False, **kwargs):
    """
    If passed no parameters this will look for all the dataframes in the user
    namespace and make them available for adding a new column to. Once a
    dataframe is chosen only the numerical columns from that dataframe will
    be available for inclusion in the new column expression.

    If you wish to allow only certain dataframes or have them show up as
    user friendly names in the menus provide that information in the first
    paramater df_info.

    To allow inclusion of text columns pass True for show_text_col.

    :param bool show_text_col: (default = False). When True columns
    containing text will be shown.

    :param list df_info: List of Lists [[object,globalname,
    userfriendly]],..]
      * object -- pandas.DataFrame
      * globalname -- string name of the object in the user global name space.
      * userfriendly -- string name to display for user selection.
      
    :keyword bool findframes: default = True. If set to false and dataframes
    are passed in dfs_info, will not search for dataframes in the user
    namespace.
    """

    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Dropdown, Label, Text, Button, Checkbox
    from ipywidgets import HTML as richLabel
    from IPython.display import display, HTML
    from IPython import get_ipython
    from .utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell, select_containing_cell, \
        delete_selected_cell

    from .utils import find_pandas_dataframe_names
    from IPython import get_ipython
    global_dict = get_ipython().user_ns
    dfs_info = []
    if isinstance(df_info,list):
        for k in df_info:
            dfs_info.append(k)
    findframes = kwargs.pop('findframes',True)
    if findframes:
        for k in find_pandas_dataframe_names():
            dfs_info.append([global_dict[k],k,k])
    friendly_to_globalname = {k[2]:k[1] for k in dfs_info}
    friendly_to_object = {k[2]:k[0] for k in dfs_info}

    #### Define GUI Elements ####

    # DataFrame Choice (Step 1)
    step1instr = Label(value = 'Select the DataFrame to work with.')
    tempopts = []
    tempopts.append('Choose')
    for k in dfs_info:
        tempopts.append(k[2])
    whichframe = Dropdown(options=tempopts,
                                description='DataFrame: ',)

    def update_columns(change):
        df = friendly_to_object[change['new']]
        tempcols = df.columns.values
        tempopt = ['Choose column to insert.']
        for k in tempcols:
            if show_text_col:
                tempopt.append(k)
            else:
                if df[k].dtype != 'O':
                    tempopt.append(k)
        whichcolumn.options = tempopt
        pass
    whichframe.observe(update_columns, names='value')
    step1 = VBox([step1instr, whichframe])

    # Step 2
    newname = Text(placeholder='Type name for new column.')
    step2instr = richLabel(
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

    step2 = VBox([step2instr, HBox([newname,
                                           insertname])])
    # Step 3
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
    step3instr = richLabel(
        value='Add the calculation to the right hand side using the menus ' \
              'to insert columns, math operations or functions. ' \
              'Your choices will replace selected ' \
              'text or insert at the current cursor position.')
    oplst = ['Choose an operation to insert.', '+', '-', '*', '/', '**',
             'exp()', 'log10()', 'ln()', 'sqrt()', 'sin()', 'cos()',
             'tan()', 'cot()', 'asin()', 'acos()', 'atan()', 'acot()']
    whichop = Dropdown(options=oplst,
                       description='Operation: ')
    def op_insert(change):
        need_numpy = False
        np_list = ['exp()', 'log10()', 'ln()', 'sqrt()', 'sin()', 'cos()',
                   'tan()', 'cot()', 'asin()', 'acos()', 'atan()',
                   'acot()']
        op = change['new']
        if op == 'Choose an operation to insert.':
            return
        if op in np_list:
            need_numpy = True
            if op == 'ln()':
                op == 'log()'
            op = 'np.' + op
        else:
            op = ' ' + op + ' '
        insert_text_into_next_cell(op)
        if need_numpy:
            move_cursor_in_current_cell(-1)
        whichop.value = 'Choose an operation to insert.'
        pass

    whichop.observe(op_insert, names='value')

    step3drops = HBox([whichcolumn, whichop])
    step3 = VBox([step3instr, step3drops])
    # Step 4
    step4instr1 = Label(
        value='Carefully check the expression for typos before selecting' \
              ' "Do it!".')
    step4instr2 = Label(
        value=' * Parentheses, brackets or braces highlighted in red ' \
              'are missing their partner.')
    step4instr3 = Label(
        value=' * Check that all double and single quotes are also ' \
              'properly paired.')
    step4instr4 = Label(
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
            text += ' # DataFrame name on last line of cell displays summary.'
            insert_newline_at_end_of_current_cell(text)
        # run composed operation
        display(JS('Jupyter.notebook.get_selected_cell().execute()'))
        select_containing_cell('newcolGUI')
        delete_selected_cell()
        pass

    gen_col_but.on_click(run_new_col_decl)
    step4instr = VBox([step4instr1, step4instr2, step4instr3,
                        step4instr4])
    step4act = VBox([show_updated_df_box, gen_col_but])
    step4 = HBox([step4instr, step4act])

    steps = Tab([step1, step2, step3, step4])
    steps.set_title(0, 'Step 1')
    steps.set_title(1, 'Step 2')
    steps.set_title(2, 'Step 3')
    steps.set_title(3, 'Step 4')

    display(HTML(
        "<h3 id ='newcolGUI' style='text-align:center;'>Pandas New Calculated "
        "Column "
        "Composer</h3>"))
    #pdComposer = VBox([whichframe, steps])
    display(steps)
    select_containing_cell('newcolGUI')
    new_cell_immediately_below()
    pass
