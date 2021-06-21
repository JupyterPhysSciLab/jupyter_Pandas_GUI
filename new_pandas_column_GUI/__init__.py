name = "new_pandas_column_GUI"
"""
This code utilizes Jupyter widgets to provide a python expression composer GUI
to generate code to add a new column to an existing Pandas DataFrame.
"""

import os

# locate directory for this package.
# absolute path to directory containing this file.
mydir = os.path.dirname(__file__)

# load any supporting files

from IPython.display import display, HTML
from IPython.display import Javascript as JS

class utils():
    import inspect

    def get_ipython_globals(self):
        """
        This operation returns the dictionary of global objects in the
        interactive namespace.
        :return: dict that is equivalent to an interactive call to Globals().
        """
        is_not_ipython_global = True
        frame = self.inspect.currentframe()
        global_dict = frame.f_globals
        try:
            namestr = global_dict['__name__']
            docstr = global_dict['__doc__']
            # print(global_dict['__name__'])
            # print(docstr)
        except KeyError:
            namestr = ''
        if (namestr == '__main__') and (
                docstr == 'Automatically created module for IPython' \
                          ' interactive environment'):
            is_not_ipython_global = False
        depth = 0
        try:
            while (is_not_ipython_global):
                nextframe = frame.f_back
                frame = nextframe
                depth += 1
                try:
                    global_dict = frame.f_globals
                    namestr = global_dict['__name__']
                    docstr = global_dict['__doc__']
                    # print(global_dict['__name__'])
                except KeyError:
                    namestr = ''
                if (namestr == '__main__') and (
                        docstr == 'Automatically created module for IPython' \
                                  ' interactive environment'):
                    is_not_ipython_global = False
        except AttributeError:
            raise AttributeError(
                'Unable to find `__main__` of interactive session. Are you ' \
                'running in Jupyter or IPython?')
        return (global_dict)

    def find_pandas_dataframe_names(self):
        """
        This operation will search the interactive name space for pandas
        DataFrame objects. It will not find DataFrames that are children
        of objects in the interactive namespace. You will need to provide
        your own operation for finding those.
        :return: List of string names for objects in the global interactive
        namespace that are pandas DataFrames.
        """
        from pandas import DataFrame as df
        dataframenames = []
        global_dict = self.get_ipython_globals()
        for k in global_dict:
            if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
                dataframenames.append(k)
        return dataframenames

class new_pandas_column_GUI():
    def __init__(self, dfs_info):
        """

        :param dfs_info: List of List of strings [[globalname,userfriendly],..]
            :globalname: string name of the object in the global name space.
            :userfriendly: string name to display for user selection.
        :return:
        """
        from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
            Dropdown, Label, Text, Button, Checkbox

        # will be set to true if needed for operations used that require numpy.
        self.need_numpy = False
        self.dfs_info = dfs_info
        self.to_globalname = {k[1]:k[0] for k in dfs_info}
        self.to_friendlyname = {k[0]:k[1] for k in dfs_info}

        #### Define GUI Elements ####

        # DataFrame Choice
        tempopts = []
        tempopts.append('Choose')
        for k in self.dfs_info:
            tempopts.append(k[1])
        self.whichframe = Dropdown(options=tempopts,
                                    description='DataFrame: ',)
        self.whichframe.observe(self.update_columns, names='value')
        # Step 1
        self.newname = Text(placeholder='Type name for new column.')
        self.step1instr = Label(
            value='Pick a name for the new column. The expression will be ' \
                  'built in the cell below. Click the "Insert" button when ' \
                  'you are satisfied with the name.')
        self.insertname = Button(description="Insert")
        self.insertname.on_click(do_insertname)

        self.step1 = VBox([self.step1instr, HBox([self.newname,
                                               self.insertname])])
        # Step 2
        self.whichcolumn = Dropdown(options=['Choose column to insert.'],
                               description='Column: ',
                               )
        self.whichcolumn.observe(self.column_insert, names='value')
        self.step2instr = Label(
            value='Choose columns and operations from the menus to insert ' \
                  'into your expression. Your choices will replace selected ' \
                  'text or insert at the current cursor position.')
        oplst = ['Choose an operation to insert.', '+', '-', '*', '/', '**',
                 'exp()', 'log()', 'ln()', 'sqrt()', 'sin()', 'cos()',
                 'tan()', 'cot()', 'asin()', 'acos()', 'atan()', 'acot()']
        self.whichop = Dropdown(options=oplst,
                           description='Operation: ')
        self.whichop.observe(op_insert, names='value')

        self.step2drops = HBox([whichcolumn, whichop])
        self.step2 = VBox([step2instr, step2drops])
        # Step 3
        self.step3instr1 = Label(
            value='Carefully check the expression for typos before selecting' \
                  ' "Do it!".')
        self.step3instr2 = Label(
            value=' * Parentheses, brackets or braces highlighted in red ' \
                  'are missing their partner.')
        self.step3instr3 = Label(
            value=' * Check that all double and single quotes are also ' \
                  'properly paired.')
        self.step3instr4 = Label(
            value=' * Check that all function calls are prefaced by ' \
                  'an \'np.\'.')
        self.show_updated_df_box = Checkbox(description='Display updated '
                                                     'dataset.',
                                       value=True)
        self.gen_col_but = Button(description='Do it!')
        self.gen_col_but.on_click(run_new_col_decl)
        self.step3instr = VBox([step3instr1, step3instr2, step3instr3,
                            step3instr4])
        self.step3act = VBox([show_updated_df_box, gen_col_but])
        self.step3 = HBox([step3instr, step3act])

        self.steps = Tab([self.step1, self.step2, self.step3])
        self.steps.set_title(0, 'Step 1')
        self.steps.set_title(1, 'Step 2')
        self.steps.set_title(2, 'Step 3')

        display(HTML(
            "<h3 style='text-align:center;'>Pandas New Calculated Column Composer</h3>"))
        self.pdComposer = VBox([self.whichframe, self.steps])
        display(self.pdComposer)
        new_cell_immediately_below()


    def new_cell_immediately_below(self):
        display(
            JS('Jupyter.notebook.focus_cell();' \
                'Jupyter.notebook.insert_cell_above();'))
        pass


    def select_cell_immediately_below(self):
        display(JS('Jupyter.notebook.select_next(true);'))


    def move_cursor_in_current_cell(self, delta):
        display(
            JS('var curPos = Jupyter.notebook.get_selected_cell().code_' \
               'mirror.doc.getCursor();' \
               'var curline = curPos.line; var curch = curPos.ch +' + str(
                delta) + ';' \
                         'Jupyter.notebook.get_selected_cell().code_mirror.' \
                         'doc.setCursor({line:curline,ch:curch});'))
        pass


    def insert_text_into_next_cell(self, text):
        display(JS('Jupyter.notebook.select_next(true);' \
                   'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
                   'replaceSelection("' + text + '");'))
        pass


    def insert_text_at_beginning_of_current_cell(self, text):
        # append \n to line insert as a separate line.
        display(
            JS('Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'setCursor({line:0,ch:0});' \
               'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'replaceSelection("' + text + '");'))
        pass


    def insert_newline_at_end_of_current_cell(self, text):
        display(
            JS('var lastline = Jupyter.notebook.get_selected_cell().' \
               'code_mirror.doc.lineCount();' \
               'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'setCursor(lastline,0);' \
               'Jupyter.notebook.get_selected_cell().code_mirror.doc.' \
               'replaceSelection("\\n' + text + '");'))
        pass

######
# Selecting which dataframe to work on
######
    def update_columns(self, change):
        from new_pandas_column_GUI import utils
        tempcols = utils.get_ipython_globals()[change['new']].columns.values
        tempopt = ['Choose column to insert.']
        for k in tempcols:
            tempopt.append(k)
        self.whichcolumn.options = tempopt
        pass

######
# Actions of GUI elements
######
    # Step 1 (Tab 1)
    def do_insertname(self, change):
        text = self.whichframe.value + '[\'' + self.newname.value + '\'] = '
        self.insert_text_into_next_cell(text)
        pass
    # Step 2 (Tab 2)
    def column_insert(self, change):
        col = change['new']
        if col == 'Choose column to insert.':
            return
        text = self.whichframe.value + '[\'' + col + '\']'
        self.insert_text_into_next_cell(text)
        self.whichcolumn.value = 'Choose column to insert.'
        pass

    def op_insert(self, change):
        global need_numpy
        np_list = ['exp()', 'log()', 'ln()', 'sqrt()', 'sin()', 'cos()',
                   'tan()', 'cot()', 'asin()', 'acos()', 'atan()', 'acot()']
        op = change['new']
        if op == 'Choose an operation to insert.':
            return
        if op in np_list:
            need_numpy = True
            op = 'np.' + op
        else:
            op = ' ' + op + ' '
        self.insert_text_into_next_cell(op)
        if need_numpy:
            self.move_cursor_in_current_cell(-1)
        self.whichop.value = 'Choose an operation to insert.'
        pass

    # Step 3 (Tab 3)
    def run_new_col_decl(self,change):
        self.select_cell_immediately_below()
        # import numpy if numpy functions used (they could have put in by hand -- insert by default?)
        text = 'import numpy as np # Necessary for function calls\\n'
        self.insert_text_at_beginning_of_current_cell(text)
        # if show updated dataframe is checked append dataframe name as last line.
        if self.show_updated_df_box.value == True:
            text = self.whichframe.value
            self.insert_newline_at_end_of_current_cell(text)
        # run composed operation
        display(JS('Jupyter.notebook.get_selected_cell().execute()'))
        # TODO: add deletion of composer cell after this is a functioning module.
        pass
