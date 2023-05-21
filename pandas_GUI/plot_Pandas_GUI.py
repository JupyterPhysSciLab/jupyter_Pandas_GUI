def plot_pandas_GUI(df_info=None, show_text_col = False, **kwargs):
    """
    If passed no parameters this will look for all the dataframes in the user
    namespace and make them available for plotting. Once a
    dataframe is chosen only the numerical columns from that dataframe will
    be available for inclusion in the plotting expression.

    This GUI produces code to use the plotly interactive plotting package.

    If you wish to allow only certain dataframes or have them show up as
    user friendly names in the menus provide that information in the first
    paramater df_info.

    To allow inclusion of text columns pass True for show_text_col.

    :param bool show_text_col: (default = False). When True columns
    containing text will be shown.

    :param list df_info: List of Lists [[object,globalname,userfriendly]],..]
      * object -- pandas.DataFrame
      * globalname -- string name of the object in the user global name space.
      * userfriendly -- string name to display for user selection.

    :keyword string figname: string used to override default python name for
    figure.

    :keyword bool findframes: default = True. If set to false and dataframes
    are passed in dfs_info, will not search for dataframes in the user
    namespace.
    """
    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Accordion, Dropdown, Label, Text, Button, Checkbox, FloatText, \
        RadioButtons, BoundedIntText, Output
    from ipywidgets import HTML as richLabel
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    from IPython import get_ipython
    from JPSLUtils.utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell, select_containing_cell, \
        delete_selected_cell, iconselector, notice_group, notebookenv, \
        replace_text_of_next_cell

    from .utils import find_pandas_dataframe_names, build_run_snip_widget
    from IPython import get_ipython
    global_dict = get_ipython().user_ns
    JPSLUtils = global_dict["JPSLUtils"]
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
    output = Output()
    with output:
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

    # Notices for the Final Check Tab.
    makeplot_notices = notice_group(['At least one trace required.',
                                     'Axes must have labels.'],
                                    'Notices:','','red')
    makeplot_notices.set_active([0,1])

    # Strings for each tab, that are combined to make the code.
    importstr = '# CODE BLOCK generated using plot_pandas_GUI().\n# See ' \
        'https://jupyterphysscilab.github.io/jupyter_Pandas_GUI.\n' \
        'from plotly import graph_objects as go\n' + str(figname) + \
        ' = go.FigureWidget(layout_template=\"simple_white\")\n'
    step1strdefault = '\n# Trace declaration(s) and trace formating\n'
    step1str = step1strdefault
    step2strdefault = '\n# Axes labels\n'
    step2str = step2strdefault
    step3strdefault = '\n# Plot formatting\n'
    step3str = step3strdefault
    # 1. Pick Traces*
    #   a. Select Y vs. X pairs* (DataFrame, X and Y, which must be from single
    #       frame.
    # Notices for the Pick Trace(s) tab.
    notice_list = [
        'Data set (DataFrame) required.',
        'X- and Y-coordinates required.',
        'Incomplete or inconsistent error specification(s).',
        'Non-default trace formatting left from previous trace.',
        'X-Error settings left from previous trace.',
        'Y-Error settings left from previous trace.',
    ]
    trace_notices = notice_group(notice_list, 'Notices:','','red')
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
    step1instracc.set_title(0,'Instructions')
    step1instracc.selected_index = None

    # DataFrame selection
    tempopts = []
    tempopts.append('Choose data set.')
    for k in dfs_info:
        tempopts.append(k[2])
    whichframe = Dropdown(options=tempopts,
                                description='DataFrame: ',)

    def update_columns(change):
        df = friendly_to_object[change['new']]
        tempcols = df.columns.values
        if change['new'] == 'Choose data set.':
            Xcoord.disabled = True
            Ycoord.disabled = True
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            trace_notices.activate_notice(0)
            trace_notices.activate_notice(1)
            add_trace_notices.value = trace_notices.notice_html()
            return
        tempopt = ['Choose column for coordinate.']
        for k in tempcols:
            if show_text_col:
                tempopt.append(k)
            else:
                if df[k].dtype != 'O':
                    tempopt.append(k)
        Xcoord.options = tempopt
        Xcoord.value = tempopt[0]
        Ycoord.options = tempopt
        Ycoord.value = tempopt[0]
        Xcoord.disabled = False
        Ycoord.disabled = False
        trace_notices.activate_notice(1)
        trace_notices.deactivate_notice(0)
        add_trace_notices.value =trace_notices.notice_html()
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
            trace_notices.deactivate_notice(1)
            add_trace_notices.value = trace_notices.notice_html()
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            modedrop.disabled = True
            colordrop.disabled = True
            yerrtype.disabled = True
            xerrtype.disabled = True
            trace_name.disabled = True
            trace_notices.activate_notice(1)
            add_trace_notices.value = trace_notices.notice_html()
        pass

    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ',
                      disabled = True)

    #   b. Trace Style (optional)
    def trace_format_update(change):
        trace_notices.deactivate_notice(3)
        add_trace_notices.value = trace_notices.notice_html()
        pass

    modedrop = Dropdown(options = ['lines','markers','lines+markers'],
                    description = 'Trace Style: ')
    modedrop.observe(trace_format_update)
    colordrop = Dropdown(options=['default','blue','orange','green','purple',
                              'red','gold','brown','black'],
                     description = 'Color: ')
    colordrop.observe(trace_format_update)
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
    filled_open.observe(trace_format_update)
    markersize = BoundedIntText(value = 6, min = 2, max = 25, step = 1,
                                description = 'Marker Size (px): ',
                                style=longdesc)
    markersize.observe(trace_format_update)
    markerhbox = HBox(children=[markerlabel,filled_open,markersize])
    markervbox = VBox(children=[markerhbox, marker_selector.box])
    line_style = Dropdown(options = ['solid','dot','dash','dashdot'],
                          description = 'Line style: ')
    line_style.observe(trace_format_update)
    line_width = BoundedIntText(value = 2, min = 1, max = 25, step = 1,
                                description = 'Linewidth (px): ',
                                style=longdesc)
    line_width.observe(trace_format_update)
    linehbox = HBox(children=[line_style,line_width])

    formatHbox1 = HBox(children=[modedrop,colordrop])
    formatVbox = VBox(children=[formatHbox1,linehbox,markervbox])
    step1formatacc = Accordion(children=[formatVbox])
    step1formatacc.set_title(0,'Trace Formatting')
    step1formatacc.selected_index = 0
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
        df = friendly_to_object[whichframe.value]
        if change['new'] == 'percent' or change['new'] == 'constant':
            yerrvalue.disabled = False
            yerrdata.disabled = True
        if change['new'] == 'data':
            yerrvalue.disabled = True
            if yerrdata.value == 'Choose error column.':
                add_trace_but.disabled = True
                add_trace_but.button_style = ''
            tempopts = ['Choose error column.']
            tempcols = df.columns.values
            for k in tempcols:
                if df[k].dtype != 'O':
                    tempopts.append(k)
            yerrdata.options=tempopts
            yerrdata.disabled = False
        if change['new'] == 'none':
            yerrvalue.disabled = True
            yerrdata.disabled = True
        if error_settings_OK():
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            trace_notices.deactivate_notice(2)
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            trace_notices.activate_notice(2)
        trace_notices.deactivate_notice(5)
        add_trace_notices.value = trace_notices.notice_html()
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
            trace_notices.deactivate_notice(2)
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            trace_notices.activate_notice(2)
        add_trace_notices.value = trace_notices.notice_html()
        pass

    yerrdata.observe(errdata_change, names = 'value')
    yerrrow1 = HBox(children=[yerrtype,yerrvalue])
    yerror = VBox(children=[yerrrow1,yerrdata])
    xerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type: ',
                        disabled = True)
    def xerr_change(change):
        df = friendly_to_object[whichframe.value]
        if change['new'] == 'percent' or change['new'] == 'constant':
            xerrvalue.disabled = False
            xerrdata.disabled = True
        if change['new'] == 'data':
            xerrvalue.disabled = True
            if xerrdata.value == 'Choose error column.':
                add_trace_but.disabled = True
                add_trace_but.button_style = ''
            tempopts = ['Choose error column.']
            tempcols = df.columns.values
            for k in tempcols:
                if df[k].dtype != 'O':
                    tempopts.append(k)
            xerrdata.options = tempopts
            xerrdata.disabled = False
        if change['new'] == 'none':
            xerrvalue.disabled = True
            xerrdata.disabled = True
        if error_settings_OK():
            add_trace_but.disabled = False
            add_trace_but.button_style = 'success'
            trace_notices.deactivate_notice(2)
        else:
            add_trace_but.disabled = True
            add_trace_but.button_style = ''
            trace_notices.activate_notice(2)
        trace_notices.deactivate_notice(4)
        add_trace_notices.value = trace_notices.notice_html()
        pass

    xerrtype.observe(xerr_change, names = 'value')
    xerrvalue = FloatText(description = '% or constant: ', disabled = True,
                          style=longdesc)
    xerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values: ',
                        disabled = True)

    xerrdata.observe(errdata_change, names = 'value')
    xerrrow1 = HBox(children=[xerrtype,xerrvalue])
    xerror = VBox(children=[xerrrow1,xerrdata])
    step1erracc = Accordion(children = [yerror,xerror])
    step1erracc.set_title(0, 'Y error bars')
    step1erracc.set_title(1, 'X error bars')
    step1erracc.selected_index = None

    # Add Trace button
    add_trace_but = Button(description = 'Add Trace',
                           disabled = True)
    def do_add_trace(change):
        nonlocal importstr, step1str, step2str, step3str
        dfname = friendly_to_globalname[whichframe.value]
        text = 'scat = go.Scatter(x = '+dfname+'[\'' \
               +Xcoord.value+'\'],'
        text += ' y = ' +dfname+'[\''+Ycoord.value+ \
                                          '\'],\n'
        text += '        mode = \''+modedrop.value+'\', name = \'' \
                                               +trace_name.value+'\','
        # in here add other formatting items using ifs.
        if colordrop.value != 'default':
            text +='\n        '
            if str(modedrop.value).find('lines') > -1:
                text += 'line_color = \''+colordrop.value+'\', '
            if str(modedrop.value).find('markers') > -1:
                text += 'marker_color = \'' + colordrop.value + '\', '
        if str(modedrop.value).find('lines') > -1:
            if line_style.value != 'solid':
                text +='\n        '
                text +='line_dash=\'' + line_style.value + '\', '
            if line_width.value != 2:
                text +='\n        '
                text +='line_width=' + str(line_width.value) + ', '
        if str(modedrop.value).find('markers') > -1:
            if markersize.value != 6:
                text += '\n        '
                text += 'marker_size=' + str(markersize.value) + ', '
            tmpmkr = icontoplotly[marker_selector.value]
            if not filled_open.value:
                text += '\n        '
                tmpmkr +='-open'
                text += 'marker_symbol=\'' + tmpmkr + '\', '
            else:
                if tmpmkr != 'circle':
                    text += '\n        '
                    text += 'marker_symbol=\'' + tmpmkr + '\', '
        if yerrtype.value != 'none':
            text +='\n        '
            if yerrtype.value == 'data':
                text += 'error_y_type=\'data\', ' \
                        'error_y_array='+dfname
                text += '[\''+yerrdata.value+'\'],'
            else:
                text += 'error_y_type=\''+yerrtype.value+'\', error_y_value='
                text += str(yerrvalue.value)+','
        if xerrtype.value != 'none':
            text +='\n        '
            if xerrtype.value == 'data':
                text += 'error_x_type=\'data\', ' \
                        'error_x_array='+dfname
                text += '[\''+xerrdata.value+'\'],'
            else:
                text += 'error_x_type=\''+xerrtype.value+'\', error_x_value='
                text += str(xerrvalue.value)+','
        text += ')\n'
        text += figname + '.add_trace(scat)\n'
        step1str += text
        if JPSLUtils.notebookenv == 'NBClassic':
            replace_text_of_next_cell(importstr+step1str+step2str+step3str)
        else:
            codearea.sniptext.value = importstr+step1str+step2str+step3str
        if (modedrop.value != 'lines') or (colordrop.value != 'default') or \
            (line_style.value != 'solid') or (line_width.value != 2) or \
            (icontoplotly[marker_selector.value] != 'circle') or \
            (not filled_open.value) or (markersize.value != 6):
            trace_notices.activate_notice(3)
        if (xerrtype.value != 'none'):
            trace_notices.activate_notice(4)
        if (yerrtype.value != 'none'):
            trace_notices.activate_notice(5)
        add_trace_notices.value = trace_notices.notice_html()
        makeplot_notices.deactivate_notice(0)
        step4noticebox.value = makeplot_notices.notice_html()
        pass
    add_trace_but.on_click(do_add_trace)

    trace_notices.set_active([0,1])
    add_trace_notices = richLabel(value = trace_notices.notice_html())
    step1tracebox = VBox(children=[whichframe,Xcoord,Ycoord,trace_name])
    step1actionbox = VBox(children=[add_trace_but, add_trace_notices])
    step1hbox = HBox(children=[step1tracebox,step1actionbox])
    step1optbox = VBox(children=[step1formatacc, step1erracc])
    step1opt = Accordion(children = [step1optbox])
    step1opt.set_title(0, 'Optional (Trace formatting, error bars...)')
    step1opt.selected_index = None
    step1 = VBox(children=[step1instracc, step1hbox, step1opt])

    # 2. Set Axes Labels (will use column names by default).
    step2instr = richLabel(value = 'You must set the axes labels to something '
                           'appropriate. For example if the X - values '
                           'represent time in seconds "Time (s)" is a good '
                           'choice. If the Y - values for the traces all '
                           'have the same units using the units as the label '
                                   'is a good choice. If the Y - values '
                                   'have different unit quantites the best '
                                   'option is probably "values" and making '
                                   'sure that the trace names used for the '
                                   'legend contain the units for each trace.')
    step2instracc = Accordion(children = [step2instr])
    step2instracc.set_title(0,'Instructions')
    step2instracc.selected_index = None
    X_label = Text(placeholder = 'Provide an X-axis label (usually has units)',
                   description = 'X-axis label: ',
                   style = longdesc,
                   layout=Layout(width='45%'))
    Y_label = Text(placeholder = 'Provide a Y-axis label (usually has units)',
                   description = 'Y-axis label: ',
                   style = longdesc,
                   layout=Layout(width='45%'))
    step2hbox = HBox(children=[X_label,Y_label])
    step2 = VBox(children=[step2instracc,step2hbox])
    # 3.Title, Format ...
    plot_title = Text(value = figname,
                       description = 'Plot title: ',
                      layout = Layout(width='80%'))
    def mirror_axes_change(change):
        if change['new']:
            mirror_ticks.disabled= False
        else:
            mirror_ticks.disabled= True
            mirror_ticks.value = False
        pass

    mirror_axes = Checkbox(value = False,
                           description = 'Display Mirror Axes',
                           style = longdesc)
    mirror_axes.observe(mirror_axes_change, names = 'value')
    mirror_ticks = Checkbox(value = False,
                            description = 'Mirror Tick Marks',
                            disabled = True)
    plot_template = Dropdown(options=['none','simple_white', 'ggplot2',
                                    'seaborn',
                                 'plotly', 'plotly_white', 'plotly_dark',
                                 'presentation', 'xgridoff', 'ygridoff',
                                 'gridon', 'simple_white+presentation',
                                      'simple_white+gridon',
                                      'simple_white+presentation+gridon'],
                        value='simple_white',
                        description = 'Plot Styling: ',
                        style = longdesc)
    step3hbox2 = HBox(children=[mirror_axes,mirror_ticks, plot_template])
    step3 = VBox(children=[plot_title,step3hbox2])

    # 4. Final Check*
    step4instr = richLabel(value = 'Things to check before clicking making ' \
                                   'the plot: <ul>' \
                                   '<li>Fix any problems listed in ' \
                                   '"Notices".</li>' \
                                   '<li>Look at the code below to make sure ' \
                                   'you have included all the traces you ' \
                                   'intended to (look for "name").</li>' \
                                   '<li>Check for any unpaired parentheses, ' \
                                   'brackets or braces.</li>' \
                                   '<li>Check that all single and double ' \
                                   'quotes are paired.</li>' \
                                   '<li>If you did any manual editing ' \
                                   'double-check for typos.</li>')
    step4noticebox = richLabel(value = makeplot_notices.notice_html())
    def makeplt_click(change):
        if JPSLUtils.notebookenv == 'NBClassic':
            text = '\n# Force save widget states so that graph will still be\n'
            text += '# available when notebook next opened in trusted state.\n'
            text += 'import time\ntime.sleep(5)'
            select_containing_cell('pandasplotGUI')
            select_cell_immediately_below()
            insert_newline_at_end_of_current_cell(text)
            jscode = 'Jupyter.actions.call("widgets:save-with-widgets");'
            text = 'JPSLUtils.OTJS(\''+jscode+'\')'
            insert_newline_at_end_of_current_cell(text)
        # run the cell to build the plot
            JPSLUtils.OTJS('Jupyter.notebook.get_selected_cell().execute();')
        # remove the GUI cell
            select_containing_cell('pandasplotGUI')
            delete_selected_cell()
        pass

    makeplotbut_lay = Layout(visibility="hidden")
    if JPSLUtils.notebookenv == 'NBClassic':
        makeplotbut_lay = Layout(visibility="visible")

    makeplotbut = Button(description = 'Make Plot',
                         layout = makeplotbut_lay,
                         disabled = True)
    makeplotbut.on_click(makeplt_click)
    step4vbox = VBox(children=[makeplotbut,step4noticebox])
    step4 = HBox(children=[step4instr,step4vbox])


    steps = Tab(children=[step1, step2, step3, step4])
    steps.set_title(0,'1. Pick Trace(s)*')
    steps.set_title(1,'2. Label Axes*')
    steps.set_title(2,'3. Title, Format ...')
    steps.set_title(3,'4. Final Check*')
    def tab_changed(change):
        nonlocal importstr, step1strdefault, step1str, step2strdefault, \
            step2str, step3strdefault, step3str
        if change['new'] ==3:
            if X_label.value == '' or Y_label.value == '':
                makeplot_notices.activate_notice(1)
                makeplotbut.disabled = True
                makeplotbut.button_style = ''
            else:
                makeplot_notices.deactivate_notice(1)
            step4noticebox.value = makeplot_notices.notice_html()
        if len(makeplot_notices.get_active()) == 0:
            makeplotbut.disabled = False
            makeplotbut.button_style = 'success'
        if change['new'] > 1:
            # update step2str
            step2str = step2strdefault
            text = figname + '.update_xaxes(title= \'' + X_label.value + '\''

            def get_mirror_text():
                if mirror_axes.value:
                    mirror_text = ', mirror = True)\n'
                    if mirror_ticks.value:
                        mirror_text = ', mirror= \'ticks\')\n'
                else:
                    mirror_text = ')\n'
                return mirror_text

            text += get_mirror_text()
            step2str += text
            text = figname + '.update_yaxes(title= \'' + Y_label.value + '\''
            text += get_mirror_text()
            step2str += text
            # update step3str
            step3str = step3strdefault
            if plot_title.value != '' or plot_template.value != 'simple_white':
                text = figname + '.update_layout(title = \'' + plot_title.value + '\', '
                text += 'template = \'' + plot_template.value + '\')\n'
                step3str += text
            text = figname + '.show()'
            if JPSLUtils.notebookenv == 'NBClassic':
                replace_text_of_next_cell(
                    importstr+step1str+step2str+step3str+text)
            else:
                codearea.sniptext.value = importstr+step1str+step2str+step3str+text

        pass

    steps.observe(tab_changed, names = 'selected_index')
    with output:
        display(steps)
    if JPSLUtils.notebookenv == 'NBClassic':
        display(output)
        select_containing_cell('pandasplotGUI')
        new_cell_immediately_below()
        insert_text_into_next_cell(importstr+step1str+step2str+step3str)
    else:
        codearea = build_run_snip_widget(
            importstr+step1str+step2str+step3str, output)
        with output:
            display(codearea)
        display(output)
    pass