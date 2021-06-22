def new_pandas_column_GUI(dfs_info):
    """

    :param dfs_info: List of List of strings [[globalname,userfriendly,
    object]
    ],..]
        :globalname: string name of the object in the global name space.
        :userfriendly: string name to display for user selection.
    :return:
    """
######
# Jupyter JS call utilities
######
    def new_cell_immediately_below():
        from IPython.display import display, HTML
        from IPython.display import Javascript as JS
        display(
            JS('Jupyter.notebook.focus_cell();' \
                'Jupyter.notebook.insert_cell_above();'))
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

    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Dropdown, Label, Text, Button, Checkbox
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    # will be set to true if needed for operations used that require numpy.
    global need_numpy
    need_numpy = False
    dfs_info = dfs_info
    global friendly_to_globalname
    friendly_to_globalname = {k[1]:k[0] for k in dfs_info}
    global_to_friendlyname = {k[0]:k[1] for k in dfs_info}
    global friendly_to_object
    friendly_to_object = {k[1]:k[2] for k in dfs_info}

    #### Define GUI Elements ####

    # DataFrame Choice
    tempopts = []
    tempopts.append('Choose')
    for k in dfs_info:
        tempopts.append(k[1])
    whichframe = Dropdown(options=tempopts,
                                description='DataFrame: ',)

    def update_columns(change):
        from new_pandas_column_GUI import utils
        global friendly_to_object
        tempcols = friendly_to_object[change['new']].columns.values
        # tempcols = utils.get_ipython_globals()[change['new']].columns.values
        tempopt = ['Choose column to insert.']
        for k in tempcols:
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
        global friendly_to_globalname
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
        global friendly_to_globalname
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
        global need_numpy
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
            global friendly_to_globalname
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

