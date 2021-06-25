def plot_pandas_GUI(dfs_info=None, show_text_col = False, **kwargs):
    """
    If passed no parameters this will look for all the dataframes in the user
    namespace and make them available for plotting. Once a
    dataframe is chosen only the numerical columns from that dataframe will
    be available for inclusion in the plotting expression.

    This GUI produces code to use the plotly interactive plotting package.

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
    :keyword figname: string used to override default python name for figure.
    :return:
    """
    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Accordion, Dropdown, Label, Text, Button, Checkbox, FloatText
    from ipywidgets import HTML as richLabel
    from IPython.display import display, HTML
    from IPython import get_ipython
    from .utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell, select_containing_cell, \
        delete_selected_cell

    if dfs_info == None:
        from .utils import find_pandas_dataframe_names
        dfs_info = []
        for k in find_pandas_dataframe_names():
            dfs_info.append([k,k])
    friendly_to_globalname = {k[1]:k[0] for k in dfs_info}

    figname = kwargs.pop('figname',None)
    from .utils import find_figure_names
    figlst = find_figure_names()
    if figname in figlst:
        raise UserWarning (str(figname) + ' already exists. Choose a '
                                          'different name for the figure.')
    if figname == None:
        figname = 'Figure_'+str(len(figlst)+1)

    #### Define GUI Elements ####
    # Those followed by a * are required.
    display(HTML(
        "<h3 id ='pandasplotGUI' style='text-align:center;'>Pandas Plot "
        "Composer</h3> <div style='text-align:center;'>Steps with a "
        "* are required.</div>"))

    # 1. Pick Traces*
    #   a. Select Y vs. X pairs* (DataFrame, X and Y, which must be from single
    #       frame.
    step1instr = richLabel(value = 'For each trace you wish to include: '
                                   '<ol><li>Select a DataFrame (Data '
                                   'set);</li>'
                                   '<li>Select the column containing the X '
                                   'values;</li>'
                                   '<li>Select the column containing the Y '
                                   'values;</li>'
                                   '<li>Provide a name for the trace if you do'
                                   ' not like the default. This text will be '
                                   'used for the legend;</li>'
                                   '<li> OPTIONAL - set additional formatting '
                                   'and error display by expanding the '
                                   'sections at the bottom of this tab;</li>'
                                   '<li>Once everything is set use the '
                                   '<b>"Add Trace"</b> button to '
                                   'include it in your plot.</li></ol>'
                                   'The code for the plot is being built in '
                                   'the cell immediately below.')

    step1instracc = Accordion(children = [step1instr])
    step1instracc.set_title(0,'Instructions.')
    step1instracc.selected_index = None

    # DataFrame selection
    tempopts = []
    tempopts.append('Choose data set.')
    for k in dfs_info:
        tempopts.append(k[1])
    whichframe = Dropdown(options=tempopts,
                                description='DataFrame: ',)

    def update_columns(change):
        dfname = friendly_to_globalname[change['new']]
        user_ns = get_ipython().user_ns
        tempcols = user_ns[dfname].columns.values
        tempopt = ['Choose column for coordinate.']
        for k in tempcols:
            if show_text_col:
                tempopt.append(k)
            else:
                if user_ns[dfname][k].dtype != 'O':
                    tempopt.append(k)
        Xcoord.options = tempopt
        Ycoord.options = tempopt
        pass
    whichframe.observe(update_columns, names='value')

    # Data selection
    Xcoord = Dropdown(options=['Choose X-coordinate.'],
                           description='X: ',
                           )

    Ycoord = Dropdown(options=['Choose Y-coordinate.'],
                           description='Y: ',
                           )
    def trace_name_update(change):
        if change['new'] != 'Choose column for coordinate.':
            trace_name.value = Ycoord.value
        pass

    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ')

    #   b. Trace Style (optional)
    modedrop = Dropdown(options = ['lines','markers','lines+markers'],
                    description = 'Style: ')
    colordrop = Dropdown(options=['default','blue','orange','green','purple',
                              'red','gold','brown','black'],
                     description = 'Color: ')
    formatHbox = HBox([modedrop,colordrop])
    step1formatacc = Accordion([formatHbox])
    step1formatacc.set_title(0,'Trace Formatting')
    step1formatacc.selected_index = None
    yerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type :')
    yerrvalue = FloatText(description = '% or constant :', disabled = True)
    yerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values :',
                        disabled = True)
    yerrrow1 = HBox([yerrtype,yerrvalue])
    yerror = VBox([yerrrow1,yerrdata])
    xerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type :')
    xerrvalue = FloatText(description = '% or constant :', disabled = True)
    xerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values :',
                        disabled = True)
    xerrrow1 = HBox([xerrtype,xerrvalue])
    xerror = VBox([xerrrow1,xerrdata])
    step1erracc = Accordion([yerror,xerror])
    step1erracc.set_title(0, 'Y error bars')
    step1erracc.set_title(1, 'X error bars')
    step1erracc.selected_index = None

    # Add Trace button
    add_trace_but = Button(description = 'Add Trace')
    def do_add_trace(change):
        text = 'scat = go.Scatter(x = '+whichframe.value+'[\'' \
               +Xcoord.value+'\'],'
        text += ' y = ' +whichframe.value+'[\''+Ycoord.value+ \
                                          '\'],\\n'
        text += '        mode = \''+modedrop.value+'\', name = \'' \
                                               +trace_name.value+'\''
        # in here add other formatting items using ifs.
        if colordrop.value != 'default':
            text +=',\\n        '
            if str(modedrop.value).find('lines') > -1:
                text += 'line_color = \''+colordrop.value+'\', '
            if str(modedrop.value).find('markers') > -1:
                text += 'marker_color = \'' + colordrop.value + '\', '
            text += '\\n'
        text += ')\\n'
        text += figname + '.add_trace(scat)'
        select_cell_immediately_below()
        insert_newline_at_end_of_current_cell(text)
        pass
    add_trace_but.on_click(do_add_trace)
    step1hbox = HBox([Xcoord,add_trace_but])
    step1optbox = VBox([step1formatacc, step1erracc])
    step1opt = Accordion([step1optbox])
    step1opt.set_title(0, 'Optional (Trace formatting, error bars...)')
    step1opt.selected_index = None
    step1 = VBox([step1instracc, whichframe,step1hbox,Ycoord,trace_name,
                  step1opt])

    # 2. Set Axes Labels (will use column names by default).

    # 3. Format, Title ...

    # 4. Check the code*

    steps = Tab([step1])
    steps.set_title(0,'1. Pick Trace(s)*')
    display(steps)
    select_containing_cell('pandasplotGUI')
    new_cell_immediately_below()
    text = 'from plotly import graph_objects as go\\n'
    text += str(figname) + ' = go.FigureWidget(' \
                          'layout_template=\\"simple_white\\")'
    insert_text_into_next_cell(text)
    pass