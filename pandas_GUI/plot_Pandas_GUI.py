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
        Accordion, Dropdown, Label, Text, Button, Checkbox, FloatText, \
        RadioButtons, BoundedIntText
    from ipywidgets import HTML as richLabel
    from IPython.display import display, HTML
    from IPython import get_ipython
    from .utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell, select_containing_cell, \
        delete_selected_cell, iconselector

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
        "Composer</h3> <div style='text-align:center;'>"
        "<span style='color:green;'>Steps with a * are required.</span> The "
        "code that will generate the plot is being "
        "built in the cell immediately below.</div><div "
        "style='text-align:center;'>This composer uses a subset of "
        "<a href ='https://plotly.com/python/line-and-scatter/#'> "
        "the plotly scatter plot</a> capabilities.</div>"))

    longdesc = {'description_width':'initial'}
    def notice_html(whichnotices):

        notice_header = '<h4 style="text-align:center;">Notices:</h4><ul>'
        notice_footer = '</ul>'
        notice_list = [
            '<li style="color:red;">Data set (DataFrame) required.</li>',
            '<li style="color:red;">X- and Y-coordinates required.</li>',
            '<li style="color:red;">Incomplete or inconsistent error '
            'specification(s).</li>',
        ]
        notice_txt = notice_header
        for j in whichnotices:
            notice_txt += notice_list[j]
        notice_txt += notice_footer
        return notice_txt

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
                                   'include it in your plot.</li></ol>')

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
        if dfname == 'Choose data set.':
            Xcoord.disabled = True
            Ycoord.disabled = True
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            add_trace_notices.value = notice_html([0,1])
            return
        tempopt = ['Choose column for coordinate.']
        for k in tempcols:
            if show_text_col:
                tempopt.append(k)
            else:
                if user_ns[dfname][k].dtype != 'O':
                    tempopt.append(k)
        Xcoord.options = tempopt
        Ycoord.options = tempopt
        Xcoord.disabled = False
        Ycoord.disabled = False
        add_trace_notices.value = notice_html([1])
        pass
    whichframe.observe(update_columns, names='value')

    # Data selection
    Xcoord = Dropdown(options=['Choose X-coordinate.'],
                           description='X: ',
                           disabled = True)

    Ycoord = Dropdown(options=['Choose Y-coordinate.'],
                           description='Y: ',
                           disabled = True)
    def trace_name_update(change):
        if change['new'] != 'Choose column for coordinate.':
            trace_name.value = Ycoord.value
        if Xcoord.value != 'Choose column for coordinate.' and Ycoord.value \
                != 'Choose column for coordinate.':
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            modedrop.disabled = False
            colordrop.disabled = False
            yerrtype.disabled = False
            xerrtype.disabled = False
            trace_name.disabled = False
            add_trace_notices.value = notice_html([])
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            modedrop.disabled = True
            colordrop.disabled = True
            yerrtype.disabled = True
            xerrtype.disabled = True
            trace_name.disabled = True
            add_trace_notices.value = notice_html([1])
        pass

    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ',
                      disabled = True)

    #   b. Trace Style (optional)
    modedrop = Dropdown(options = ['lines','markers','lines+markers'],
                    description = 'Trace Style: ')
    colordrop = Dropdown(options=['default','blue','orange','green','purple',
                              'red','gold','brown','black'],
                     description = 'Color: ')
    iconlist = ['circle', 'square', 'caret-up', 'star', 'plus', 'times',
                'caret-down', 'caret-left', 'caret-right']
    icontoplotly = {'circle': 'circle', 'square': 'square',
                   'caret-up': 'triangle-up', 'plus': 'cross',
                   'times': 'x', 'caret-down': 'triangle-down',
                   'caret-left': 'triangle-left', 'caret-right':
                       'triangle-right', 'star': 'star'}
    markerlabel = Label('Marker Choices: ')
    marker_selector = iconselector(iconlist, selected = 'circle')
    filled_open = Checkbox(value = True,
                           description = 'Filled (uncheck for open)',
                           style={'description_width':'initial'})
    markersize = BoundedIntText(value = 6, min = 2, max = 25, step = 1,
                                description = 'Marker Size (px): ',
                                style=longdesc)
    markerhbox = HBox([markerlabel,filled_open,markersize])
    markervbox = VBox([markerhbox, marker_selector.box])
    line_style = Dropdown(options = ['solid','dot','dash','dashdot'],
                          description = 'Line style: ')
    line_width = BoundedIntText(value = 2, min = 1, max = 25, step = 1,
                                description = 'Linewidth (px): ',
                                style=longdesc)
    linehbox = HBox([line_style,line_width])

    formatHbox1 = HBox([modedrop,colordrop])
    formatVbox = VBox([formatHbox1,linehbox,markervbox])
    step1formatacc = Accordion([formatVbox])
    step1formatacc.set_title(0,'Trace Formatting')
    step1formatacc.selected_index = None
    yerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type: ',
                        disabled = True)

    def error_settings_OK():
        check = True
        if (yerrtype.value == 'data') and (yerrdata.value == 'Choose error '
                                                        'column.'):
            check = False
        if (xerrtype.value == 'data') and (xerrdata.value == 'Choose error '
                                                        'column.'):
            check = False
        if (yerrtype.value == 'none' or yerrtype.value == 'percent' or
            yerrtype.value == 'constant') and (xerrtype.value == 'none' or
                                               xerrtype.value == 'percent'
                                               or xerrtype.value =='constant'):
            check = True
        return check

    def yerr_change(change):
        dfname = friendly_to_globalname[whichframe.value]
        user_ns = get_ipython().user_ns
        if change['new'] == 'percent' or change['new'] == 'constant':
            yerrvalue.disabled = False
            yerrdata.disabled = True
        if change['new'] == 'data':
            yerrvalue.disabled = True
            if yerrdata.value == 'Choose error column.':
                add_trace_but.disabled = True
                add_trace_but.button_style = ''
            tempopts = ['Choose error column.']
            tempcols = user_ns[dfname].columns.values
            for k in tempcols:
                if user_ns[dfname][k].dtype != 'O':
                    tempopts.append(k)
            yerrdata.options=tempopts
            yerrdata.disabled = False
        if change['new'] == 'none':
            yerrvalue.disabled = True
            yerrdata.disabled = True
        if error_settings_OK():
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            add_trace_notices.value = notice_html([])
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            add_trace_notices.value = notice_html([2])
        pass

    yerrtype.observe(yerr_change, names = 'value')

    yerrvalue = FloatText(description = '% or constant: ', disabled = True,
                          style=longdesc)
    yerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values: ',
                        disabled = True)

    def errdata_change(change):
        if error_settings_OK():
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            add_trace_notices.value = notice_html([])
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            add_trace_notices.value = notice_html([2])
        pass

    yerrdata.observe(errdata_change, names = 'value')
    yerrrow1 = HBox([yerrtype,yerrvalue])
    yerror = VBox([yerrrow1,yerrdata])
    xerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type: ',
                        disabled = True)
    def xerr_change(change):
        dfname = friendly_to_globalname[whichframe.value]
        user_ns = get_ipython().user_ns
        if change['new'] == 'percent' or change['new'] == 'constant':
            xerrvalue.disabled = False
            xerrdata.disabled = True
        if change['new'] == 'data':
            xerrvalue.disabled = True
            if xerrdata.value == 'Choose error column.':
                add_trace_but.disabled = True
                add_trace_but.button_style = ''
            tempopts = ['Choose error column.']
            tempcols = user_ns[dfname].columns.values
            for k in tempcols:
                if user_ns[dfname][k].dtype != 'O':
                    tempopts.append(k)
            xerrdata.options = tempopts
            xerrdata.disabled = False
        if change['new'] == 'none':
            xerrvalue.disabled = True
            xerrdata.disabled = True
        if error_settings_OK():
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            add_trace_notices.value = notice_html([])
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            add_trace_notices.value = notice_html([2])
        pass

    xerrtype.observe(xerr_change, names = 'value')
    xerrvalue = FloatText(description = '% or constant: ', disabled = True,
                          style=longdesc)
    xerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values: ',
                        disabled = True)

    xerrdata.observe(errdata_change, names = 'value')
    xerrrow1 = HBox([xerrtype,xerrvalue])
    xerror = VBox([xerrrow1,xerrdata])
    step1erracc = Accordion([yerror,xerror])
    step1erracc.set_title(0, 'Y error bars')
    step1erracc.set_title(1, 'X error bars')
    step1erracc.selected_index = None

    # Add Trace button
    add_trace_but = Button(description = 'Add Trace',
                           disabled = True)
    def do_add_trace(change):
        text = 'scat = go.Scatter(x = '+whichframe.value+'[\'' \
               +Xcoord.value+'\'],'
        text += ' y = ' +whichframe.value+'[\''+Ycoord.value+ \
                                          '\'],\\n'
        text += '        mode = \''+modedrop.value+'\', name = \'' \
                                               +trace_name.value+'\','
        # in here add other formatting items using ifs.
        if colordrop.value != 'default':
            text +='\\n        '
            if str(modedrop.value).find('lines') > -1:
                text += 'line_color = \''+colordrop.value+'\', '
            if str(modedrop.value).find('markers') > -1:
                text += 'marker_color = \'' + colordrop.value + '\', '
        if yerrtype.value != 'none':
            text +='\\n        '
            if yerrtype.value == 'data':
                text += 'error_y_type=\'data\', ' \
                        'error_y_array='+whichframe.value
                text += '[\''+yerrdata.value+'\'],'
            else:
                text += 'error_y_type=\''+yerrtype.value+'\', error_y_value='
                text += str(yerrvalue.value)+','
        if xerrtype.value != 'none':
            text +='\\n        '
            if xerrtype.value == 'data':
                text += 'error_x_type=\'data\', ' \
                        'error_x_array='+whichframe.value
                text += '[\''+xerrdata.value+'\'],'
            else:
                text += 'error_x_type=\''+xerrtype.value+'\', error_x_value='
                text += str(xerrvalue.value)+','
        text += ')\\n'
        text += figname + '.add_trace(scat)'
        select_cell_immediately_below()
        insert_newline_at_end_of_current_cell(text)
        pass
    add_trace_but.on_click(do_add_trace)

    add_trace_notices = richLabel(value = notice_html([0,1]))
    step1tracebox = VBox([whichframe,Xcoord,Ycoord,trace_name])
    step1actionbox = VBox([add_trace_but, add_trace_notices])
    step1hbox = HBox([step1tracebox,step1actionbox])
    step1optbox = VBox([step1formatacc, step1erracc])
    step1opt = Accordion([step1optbox])
    step1opt.set_title(0, 'Optional (Trace formatting, error bars...)')
    step1opt.selected_index = None
    step1 = VBox([step1instracc, step1hbox, step1opt])

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