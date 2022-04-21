import numpy as np

def calcresid(result):
    '''
    lmfit has empty values for residuals where the weighting is infinite or not defined.
    This calculates all the residuals based on the actual data and fit results.

    :param ModelResult result: An lmfit ModelResult.

    :return np.array residuals: The residuals.
    '''
    import numpy as np
    import lmfit as lmfit
    resid = []
    for i in range(0, len(results.data)):
        resid.append(results.data[i] - results.best_fit[i])
    return np.array(resid)

def fit_pandas_GUI(df_info=None, show_text_col = False, **kwargs):
    """
    If passed no parameters this will look for all the dataframes in the user
    namespace and make them available for plotting. Once a
    dataframe is chosen only the numerical columns from that dataframe will
    be available for inclusion in the plotting expression.

    This GUI produces code to use the lmfit package to fit data and the plotly
    interactive plotting package to display the results.

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
      
    :keyword string figname: string used to override default python name for
    figure.

    :keyword string fitname: string used to override default python name for
    fit.
    
    :keyword bool findframes: default = True. If set to false and dataframes
    are passed in dfs_info, will not search for dataframes in the user
    namespace.
    """
    from ipywidgets import Layout, Box, HBox, VBox, GridBox, Tab, \
        Accordion, Dropdown, Label, Text, Button, Checkbox, FloatText, \
        RadioButtons, BoundedIntText
    from ipywidgets import HTML as richLabel
    from ipywidgets import HTMLMath as texLabel
    import plotly.graph_objects as go
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    from IPython import get_ipython
    from .utils import new_cell_immediately_below,\
        select_cell_immediately_below, move_cursor_in_current_cell, \
        insert_text_into_next_cell, insert_text_at_beginning_of_current_cell, \
        insert_newline_at_end_of_current_cell, select_containing_cell, \
        delete_selected_cell, iconselector, notice_group, \
        replace_text_of_current_cell
    import JPSLUtils
    from lmfit import models

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

    fitname = kwargs.pop('fitname',None)
    from .utils import find_fit_names
    fitlst = find_fit_names()
    if fitname in fitlst:
        raise UserWarning (str(fitname) + ' already exists. Choose a '
                                          'different name for the fit.')
    if fitname == None:
        fitname = 'Fit_'+str(len(fitlst)+1)

    figname = kwargs.pop('figname',None)
    from .utils import find_figure_names
    figlst = find_figure_names()
    if figname in figlst:
        raise UserWarning (str(figname) + ' already exists. Choose a '
                                          'different name for the figure.')
    if figname == None:
        figname = str(fitname) + '_Figure'

    fitmodels = ['LinearModel','PolynomialModel','ExponentialModel',
                 'GaussianModel','SineModel']
    fitmodeleqns = {
    'LinearModel':r'$fit = \color{red}{a}x+\color{red}{b}$, where $\color{'
                  r'red}{a}$ = slope, $\color{red}{b}$ = intercept',
    'PolynomialModel': r'$fit = \sum_{n=0}^{\le7}{\color{red}{c_n}x^n} = '
                       r'\color{red}{c_0} + \color{red}{c_1}x + \color{red}{'
                       r'c_2}x^2 + ...$',
    'ExponentialModel': r'$fit = \color{red}{A} \exp \left( \frac{-x} ' \
                        r'{\color{red}{\tau}}\right)$, where $\color{red}{A}$ '
                        r'= amplitude, $ \color{red}{\tau}$ = decay',
    'GaussianModel': r'$fit = \frac{\color{red}{A}}{\color{red}{\sigma} ' \
                     r'\sqrt{2 \pi}} \exp \left( \frac{-(x-\color{red}' \
                     r'{\mu})^2}{2 \color{red}{\sigma}^2} \right)$, where ' \
                     r'$\color{red}{A}$ = amplitude, $\color{red}{\sigma}$ = sigma, '
                     r'$\color{red}{\mu}$ = center',
        'SineModel': r'$fit = \color{red}{A} \sin \left ( \color{red}{f}x + '
                     r'\color{red}{\phi} \right)$, '
                     r'where $\color{red}{A}$ = ' \
                     r'amplitude, $\color{red}{f}$ = frequency, '\
                     r'$\color{red}{\phi}$ = shift'
    }

    def polymodelresultstr(resultname):
        template = r'' \
          'fitstr = r\'$fit = \'\\n' \
          'termcount = 0\\n' \
          'for k in %result.params.keys():\\n' \
          '    pwr = int(str(k)[-1:])\\n' \
          '    if %result.params[k].vary:\\n' \
          '        if termcount > 0:\\n' \
          '            fitstr += \' + \'\\n' \
          '        fitstr += r\'(\\\color{red}{\'+rue.latex_rndwitherr(' \
                                         '%result.params[k].value,\\n' \
          '                               %result.params[k].stderr, ' \
                                         'errdig=1, lowmag=-3)+\'})\'\\n' \
          '        if pwr == 1:\\n' \
          '            fitstr += \'x\'\\n' \
          '        if pwr > 1:\\n' \
          '            fitstr += \'x^\'+str(pwr)\\n' \
          '        termcount+=1\\n' \
          '    else:\\n' \
          '        if %result.params[k].value!=0:\\n' \
          '            if termcount > 0:\\n' \
          '                fitstr += \'+\'\\n' \
          '            fitstr += r\'(\\\color{blue}{\'+str(' \
                                         '%result.params[k].value)+\'})\'\\n' \
          '            termcount +=1\\n' \
          '            if pwr == 1:\\n' \
          '                fitstr += \'x\'\\n' \
          '            if pwr > 1:\\n' \
          '                fitstr += \'x^\'+str(pwr)\\n' \
          'fitstr+=\'$\'\\n' \
          'captionstr=\'<p>Use the command <code>%result</code> as the' \
          'last line of a code cell for more details.</p>\'\\n' \
          'display(HTML(fitstr+captionstr))'
        return template.replace('%result', str(resultname))

    def linmodelresultstr(resultname):
        template = r'' \
       'slopestr = ''\'\'\\n' \
       'interceptstr = ''\'\'\\n' \
       'for k in %results.params.keys():\\n' \
       '    if %results.params[k].vary:\\n' \
       '        paramstr = r\'(\\\color{red}{\'+rue.latex_rndwitherr(' \
                   '%results.params[k].value,\\n' \
       '                                       %results.params[k].stderr,\\n' \
       '                                       errdig=1,lowmag=-3)+\'})\'\\n' \
       '    else:\\n' \
       '        paramstr = r\'\\\color{blue}{\'+str(%results.params[' \
                   'k].value,' \
                   '\\n' \
       '                                       )+\'}\'\\n' \
       '    if k == \'slope\':\\n' \
       '        slopestr = paramstr\\n' \
       '    if k == \'intercept\' and %results.params[k].value != 0:\\n' \
       '        interceptstr = \' + \' + paramstr\\n' \
       'fitstr = r\'$fit = \'+slopestr + \'x\' + interceptstr + \'$\'\\n' \
       'captionstr = \'<p>Use the command <code>%results</code> as the ' \
       'last line of a code cell for more details.</p>\'\\n' \
       'display(HTML(fitstr+captionstr))'
        return template.replace('%results', resultname)

    def expmodelresultstr(resultname):
        template = r'' \
        'ampstr = ''\'\'\\n' \
        'decaystr = ''\'\'\\n' \
        'for k in %results.params.keys():\\n' \
        '    if %results.params[k].vary:\\n' \
        '        paramstr = r\'(\\\color{red}{\'+rue.latex_rndwitherr(' \
        '%results.params[k].value,\\n' \
        '                                 %results.params[k].stderr,\\n' \
        '                                 errdig=1, lowmag=-3)+\'})\'\\n' \
        '    else:\\n' \
        '        paramstr = r\'\\\color{blue}{\'+str(%results.params[' \
                                               'k].value, \\n' \
        '                                       )+\'}\'\\n' \
        '    if k == \'amplitude\':\\n' \
        '        ampstr = paramstr\\n' \
        '    if k == \'decay\':\\n' \
        '        decaystr = paramstr\\n' \
        'fitstr = r\'$$fit = \'+ampstr+r\'\\\exp \\\left( %FRAC{-x}' \
                        r'{\'+decaystr+r\'}\\right)$$\'\n' \
        'captionstr = \'<p>Use the command <code>%results</code> as the ' \
        'last line of a code cell for more details.</p>\'\\n' \
        'display(HTML(fitstr+captionstr))'
        return template.replace('%results',resultname).replace('%FRAC',r'\\frac')

    def gausmodelresultstr(resultname):
        # TODO
        template = r'' \
        'ampstr = ''\'\'\\n' \
        'centstr = ''\'\'\\n' \
        'sigmastr = ''\'\'\\n' \
        'for k in %results.params.keys():\\n' \
        '    if %results.params[k].vary:\\n' \
        '        paramstr = r\'(\\\color{red}{\'+rue.latex_rndwitherr(' \
                                          '%results.params[k].value,\\n' \
        '                                 %results.params[k].stderr,\\n' \
        '                                 errdig=1, lowmag=-3)+\'})\'\\n' \
        '    else:\\n' \
        '        paramstr = r\'\\\color{blue}{\'+str(%results.params[' \
                                               'k].value, \\n' \
        '                                       )+\'}\'\\n' \
        '    if k == \'amplitude\':\\n' \
        '        ampstr = paramstr\\n' \
        '    if k == \'center\':\\n' \
        '        centstr = paramstr\\n' \
        '    if k == \'sigma\':\\n' \
        '        sigmastr = paramstr\\n' \
        'fitstr = r\'$$fit = %FRAC{\'+ampstr+\'}{' \
                   r'\'+sigmastr+r\'\\\sqrt{2\\\pi}}\\\exp \\\left( %FRAC{' \
                   r'-\\left[x-\'+centstr+r\'\\right]^2}' \
                   r'{2\'+sigmastr+r\'^2}\\right)$$\'\n' \
        'captionstr = \'<p>Use the command <code>%results</code> as the ' \
        'last line of a code cell for more details.</p>\'\\n' \
        'display(HTML(fitstr+captionstr))'
        return template.replace('%results',resultname).replace('%FRAC',r'\\frac')

    def sinmodelresultstr(resultname):
        template = r'' \
       'ampstr = \'\'\\n' \
       'freqstr = \'\'\\n' \
       'shiftstr = \'\'\\n' \
       'for k in %results.params.keys():\\n' \
       '    if %results.params[k].vary:\\n' \
       '        paramstr = \'(\\\color{red}{\'+rue.latex_rndwitherr(' \
                   '%results.params[k].value,\\n' \
       '                                       %results.params[k].stderr,\\n' \
       '                                       errdig=1,lowmag=-3)+\'})\'\\n' \
       '    else:\\n' \
       '        paramstr = \'\\\color{blue}{\'+str(%results.params[k].value' \
                   ')+\'}\'\\n' \
       '    if k == \'amplitude\':\\n' \
       '        ampstr = paramstr\\n' \
       '    if k == \'frequency\':\\n' \
       '        freqstr = paramstr\\n' \
       '    if k == \'shift\' and %results.params[k].value != 0:\\n' \
       '        shiftstr = \' + \' + paramstr\\n' \
       'fitstr = r\'$fit = \'+ampstr + \'sin[\' + freqstr + \'x\' + shiftstr + \']$\'\\n' \
       'captionstr = \'<p>Use the command <code>%results</code> as the ' \
       'last line of a code cell for more details.</p>\'\\n' \
       'display(HTML(fitstr+captionstr))'
        return template.replace('%results', resultname)

    fitresultstrs = {
    'LinearModel': linmodelresultstr,
    'PolynomialModel': polymodelresultstr,
    'ExponentialModel': expmodelresultstr,
    'GaussianModel': gausmodelresultstr,
    'SineModel': sinmodelresultstr
    }

    importstr = r'# CODE BLOCK generated using fit_pandas_GUI(). See '\
                r'https://github.com/JupyterPhysSciLab/jupyter_Pandas_GUI.\n' \
                r'# Imports (no effect if already imported)\n' \
                r'import numpy as np\n' \
                r'import lmfit as lmfit\n' \
                r'import round_using_error as rue\n' \
                r'import copy as copy\n' \
                r'from plotly import graph_objects as go\n' \
                r'from IPython.display import HTML\n\n'
    step1str = ''
    step2str = ''
    step3str = ''
    step4str = ''
    step5str = ''
    step6str = ''
    range_chosen = False
    #### Define GUI Elements ####
    # Those followed by a * are required.
    display(HTML(
        "<h3 id ='pandasfitGUI' style='text-align:center;'>Pandas Fit "
        "Composer</h3> <div style='text-align:center;'>"
        "<span style='color:green;'>Steps with a * are required.</span> The "
        "code that will generate the fit is being "
        "built in the cell immediately below.</div><div "
        "style='text-align:center;'>This composer uses a subset of "
        "<a href ='https://lmfit.github.io/lmfit-py/'> the lmfit package</a>"
        " and <a href ='https://plotly.com/python/line-and-scatter/#'> "
        "the plotly scatter plot</a> capabilities.</div>"))

    longdesc = {'description_width':'initial'}

    # Notices for the Final Check Tab.
    makeplot_notices = notice_group(['Need data to fit',
                                     'Need a fit model',
                                     'Axes must have labels.'],
                                    'Notices:','','red')
    makeplot_notices.set_active([0,1,2])

    # 1. Pick and variables to fit and fit model
    #   a. Select Y vs. X (DataFrame, X and Y, which must be from single
    #       frame.
    # Notices for the Pick Trace(s) tab.
    notice_list = [
        'Data set (DataFrame) required.',
        'X- and Y-values required.',
    ]
    trace_notices = notice_group(notice_list, 'Notices:','','red')
    trace_notices.set_active([0,1])
    step1instr = richLabel(value = '<ol><li>Select a DataFrame (Data '
                                   'set);</li>'
                                   '<li>Select the column containing the X '
                                   'values;</li>'
                                   '<li>Select the column containing the Y '
                                   'values (what is being fit);</li>'
                                   '<li>Provide a name for the trace if you do'
                                   ' not like the default. This text will be '
                                   'used for the legend;</li></ol>'
                           )
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
        if change['new'] == 'Choose data set.':
            Xcoord.disabled = True
            Ycoord.disabled = True
            trace_notices.activate_notice(0)
            trace_notices.activate_notice(1)
            trace_notices.activate_notice(2)
            add_trace_notices.value = trace_notices.notice_html()
            return
        df = friendly_to_object[change['new']]
        tempcols = df.columns.values
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
            yerrtype.disabled = False
            trace_name.disabled = False
            trace_notices.deactivate_notice(1)
            add_trace_notices.value = trace_notices.notice_html()
        else:
            yerrtype.disabled = True
            trace_name.disabled = True
            trace_notices.activate_notice(1)
            add_trace_notices.value = trace_notices.notice_html()
        pass
    Xcoord.observe(trace_name_update,names='value')
    Ycoord.observe(trace_name_update,names='value')

    # Trace name
    trace_name = Text(placeholder = 'Trace name for legend',
                      description = 'Trace name: ',
                      disabled = True)

    trace_notices.set_active([0,1])
    add_trace_notices = richLabel(value = trace_notices.notice_html())
    step1tracebox = VBox([whichframe,Xcoord,Ycoord,trace_name])
    step1actionbox = VBox([add_trace_notices])
    step1hbox = HBox([step1tracebox,step1actionbox])
    step1 = VBox([step1instracc, step1hbox])

    # 2. Set data uncertainty
    step2instr = richLabel(value = 'If you know the uncertainty in your data '
                                   'values (Y-values)you should '
                                   'specify it, as the uncertainty impacts '
                                   'the final uncertainty in the fit '
                                   'parameters. '
                                   'If you do not know the uncertainty of '
                                   'your data leave the "Error Type" as '
                                   '"none". In this case all the data values '
                                   'will be equally weighted during the fit. '
                                   'Alternatives are: a constant uncertainty '
                                   'that is the same for every data point; a '
                                   'percentage of each value; data (a '
                                   'column) specifying the uncertainty for '
                                   'every data point.')

    yerrtype = Dropdown(options = ['none','percent','constant','data'],
                        description = 'Error Type: ',
                        disabled = True)

    def error_settings_OK():
        check = True
        if (yerrtype.value == 'data') and (yerrdata.value == 'Choose error '
                                                        'column.'):
            check = False
        return check

    def yerr_change(change):
        df = friendly_to_object[whichframe.value]
        if change['new'] == 'percent' or change['new'] == 'constant':
            yerrvalue.disabled = False
            yerrdata.disabled = True
        if change['new'] == 'data':
            yerrvalue.disabled = True
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
        add_trace_notices.value = trace_notices.notice_html()
        pass

    yerrtype.observe(yerr_change, names = 'value')

    yerrvalue = FloatText(description = '% or constant: ', disabled = True,
                          style=longdesc, value=1.0)
    yerrdata = Dropdown(options = ['Choose error column.'],
                        description = 'Error values: ',
                        disabled = True)

    def errdata_change(change):
        if error_settings_OK():
            #trace_notices.deactivate_notice(2)
            pass
        else:
            #trace_notices.activate_notice(2)
            pass
        add_trace_notices.value = trace_notices.notice_html()
        pass

    yerrdata.observe(errdata_change, names = 'value')
    yerrrow1 = HBox([yerrtype,yerrvalue])
    yerror = VBox([yerrrow1,yerrdata])
    step2instracc = Accordion(children=[step2instr])
    step2instracc.selected_index = None
    step2 = VBox([step2instr,yerror])

    # 3. Set fit parameters
    step3instr = richLabel(value = '<ol><li>Choose the fit type ('
                                   'functional form). <span '
                                   'style="color:red">Red symbols are '
                                   'the fit parameters.</span></li>'
                                   '<li>You may use the default settings for '
                                   'the '
                                   'initial guesses and parameter ranges or '
                                   'you may set them.</li>'
                                   '<li>To fix a value at the '
                                   'initial guess select the "fix" checkbox. '
                                   'You must provide an initial guess if you '
                                   'fix a parameter.</li></ol>')
    step3instracc = Accordion(children = [step3instr])
    step3instracc.set_title(0,'Instructions')
    step3instracc.selected_index = None
    # get selected fit model and update parameters list.
    modeldrop = Dropdown(options=fitmodels)
    modeleqn = texLabel(value = fitmodeleqns[modeldrop.value])
    def getcurrmodel_param(modelname, params_set):
        '''
        Using the model name return ipywidgets for setting the fit 
        parameters and constraints, populated with the default values.
        :param string modelname: The string name for the lmfit model.
        :param VBox params_set: The VBox containing the HBoxes for parameter
            guesses and constraints.
        :return VBox: params_set with fields reset and those available visible.
        '''
        currmodel = getattr(models,modelname)()
        currmodel_param = []
        labeltext = ''
        fix = False
        value = np.nan
        min = -np.inf
        max = np.inf
        expr = None  # Not used, maybe for arbitrary functions.
        for i in range(0,8):
            fix = False
            if modelname == 'PolynomialModel':
                # PolynomialModel requires that the initial value be a number
                value = 0
            else:
                value = np.nan
            min = -np.inf
            max = np.inf
            expr = None  # Not used, maybe for arbitrary functions.
            if i < len(currmodel.param_names):
                labeltext = str(currmodel.param_names[i])
                hints = currmodel.param_hints.get(labeltext,None)
                if isinstance(hints,dict):
                    fix = not(hints.get('vary',True))
                    value = hints.get('value',np.nan)
                    min = hints.get('min',-np.inf)
                    max = hints.get('max',np.inf)
                    expr = hints.get('expr',None)
                params_set.children[i].layout.display=''
                if modelname == 'ExponentialModel':
                    df = friendly_to_object[whichframe.value]
                    xvals = df[Xcoord.value]
                    yvals = df[Ycoord.value]
                    if labeltext == 'amplitude':
                        value = np.mean(yvals)
                    if labeltext == 'decay':
                        value = (np.max(xvals) - np.min(xvals))/3.0
            else:
                labeltext = str(i)
                params_set.children[i].layout.display='none'
            params_set.children[i].children[0].value = labeltext+':'
            params_set.children[i].children[1].children[0].value = fix
            params_set.children[i].children[1].children[1].value = value
            params_set.children[i].children[1].children[2].value = min
            params_set.children[i].children[1].children[3].value = max
        pass

    def make_param_set():
        '''
        Creates at VBox with 7 parameters each having fields in an HBox:
        1. fixcheck (checkbox for fixing the value)
        2. valuefield (floatText for setting the value)
        3. minfield (floatText for setting the minimum allowed value)
        4. maxfield (floatText for setting the maximum allowed value)
        By default the all VBox components have their `layout.display=none`.
        :return: VBox
        '''
        currmodel_param=[]
        for i in range (0,8):
            fixcheck = Checkbox(value=False,
                                description='Fix (hold)',
                                disabled=False,
                                style=longdesc)
            valuefield = FloatText(value=np.nan,
                                   description='Value: ',
                                   disabled=False,
                                   style=longdesc)
            minfield = FloatText(value=-np.inf,
                                 description='Min: ',
                                 disabled=False,
                                 style=longdesc)
            maxfield = FloatText(value=np.inf,
                                 description='Max: ',
                                 disabled=False,
                                 style=longdesc)
            paramlabel = Label(value = str(i)+':',style=longdesc)
            parambox = VBox([paramlabel,HBox([fixcheck,valuefield,minfield,
                                    maxfield])])
            parambox.layout.display = 'none'
            currmodel_param.append(parambox)
        params_set = VBox(currmodel_param)
        return params_set

    def modeldrop_change(change):
        modeleqn.value=fitmodeleqns[modeldrop.value]
        getcurrmodel_param(modeldrop.value,params_set)
        pass
    modeldrop.observe(modeldrop_change, names = 'value')
    params_set = make_param_set()
    getcurrmodel_param(modeldrop.value, params_set)
    step3 = VBox([step3instracc,HBox([modeldrop,modeleqn]),params_set])

    # 5.Title, Axes, Format ...
    step5instr = richLabel(value = 'You must set the axes labels to something '
                           'appropriate. For example if the X - values '
                           'represent time in seconds "Time (s)" is a good '
                           'choice. Likewise, choose an appropriate label '
                                   'for the Y - axis.')
    plot_title = Text(value = figname,
                       description = 'Plot title: ',
                      layout = Layout(width='80%'))
    X_label = Text(placeholder = 'Provide an X-axis label (usually has units)',
                   description = 'X-axis label: ',
                   style = longdesc,
                   layout=Layout(width='45%'))
    Y_label = Text(placeholder = 'Provide a Y-axis label (usually has units)',
                   description = 'Y-axis label: ',
                   style = longdesc,
                   layout=Layout(width='45%'))
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
    step5hbox1 = HBox([X_label, Y_label])
    step5hbox2 = HBox([mirror_axes,mirror_ticks, plot_template])
    step5 = VBox([step5instr, plot_title, step5hbox1, step5hbox2])

    # 4. Pick Fit Range(s)
    step4instr = richLabel(value ='This step is optional. '
                                  'If you define no range(s) all data '
                                  'points will be used in the fit. <ul>'
                                  '<li> Click on points to select the '
                                  'beginning and ending of each range of '
                                  'data to include in the fit.</li>'
                                  '<li> Hold down the `ctrl` key while '
                                  'clicking on a point to deselect it.</li>'
                                  '<li> Nearest neighbor pairs of points '
                                  'starting with the lowest point index '
                                  'number are used to define each range. If '
                                  'you select an odd number of points, '
                                  'the last point will be ignored.</li>'
                                  '<li> Check the `Extend fitted function '
                                  'plot` box if you want to display '
                                  'calculations of the fitted function and '
                                  'residuals in regions that were not fit '
                                  'to.</li></ul>')
    extend_fit = Checkbox(value=False,
                           description='Extend fitted function plot',
                           style=longdesc)
    range_plot =  go.FigureWidget(layout_template='simple_white')
    range_plot_line_color = 'blue'
    range_plot_hilight = 'cyan'
    range_plot_marker_size = 6
    range_plot_hilight_size = 20
    ranges=[]
    def update_range_point(trace, points, selector):
        # size and color must be done separately as they may not be updated
        # in sync.
        from collections import Iterable
        if not isinstance(trace['marker']['size'],Iterable):
            s = [range_plot_marker_size]*len(trace['x'])
        else:
            s = list(trace['marker']['size'])
        if (not isinstance(trace['marker']['color'],Iterable)) or isinstance(
                trace['marker']['color'],str):
            c = [range_plot_line_color]*len(trace['x'])
        else:
            c = list(trace['marker']['color'])
        for i in points.point_inds:
            if selector.ctrl:
                c[i]=range_plot_line_color
                s[i] = range_plot_marker_size
            else:
                c[i] = range_plot_hilight
                s[i] = range_plot_hilight_size
        with range_plot.batch_update():
            trace.marker.color = c
            trace.marker.size = s
        pass
    step4instacc = Accordion(children =[step4instr])
    step4instacc.set_title(0,'Instructions (optional step)')
    step4instacc.selected_index = None
    step4 = VBox([step4instacc,extend_fit,range_plot])

    # 6. Final Check*
    step6instr = richLabel(value = 'Things to check before clicking "Do '
                                   'Fit": <ul>'
                                   '<li>Fix any problems listed in '
                                   '"Notices".</li>'
                                   '<li>Check for any unpaired parentheses, '
                                   'brackets or braces (usually highlighted '
                                   'in red).</li>'
                                   '<li>Check that all single and double '
                                   'quotes are paired.</li>'
                                   '<li>If you did any manual editing '
                                   'double-check for typos.</li>')
    step6noticebox = richLabel(value = makeplot_notices.notice_html())
    def dofit_click(change):
        select_cell_immediately_below()
        # run the cell to build the plot
        JPSLUtils.OTJS('Jupyter.notebook.get_selected_cell().execute()')
        # remove the GUI cell
        select_containing_cell('pandasfitGUI')
        delete_selected_cell()
        pass
    dofitbut = Button(description = 'Do Fit', disabled = True)
    dofitbut.on_click(dofit_click)
    step6vbox = VBox([dofitbut,step6noticebox])
    step6 = HBox([step6instr,step6vbox])


    steps = Tab([step1, step2, step3, step4, step5, step6])
    steps.set_title(0,'1. Pick Data*')
    steps.set_title(1,'2. Data Uncertainty*')
    steps.set_title(2,'3. Set up Model*')
    steps.set_title(3,'4. Pick Fit Range(s)')
    steps.set_title(4, '5. Axes & Format*')
    steps.set_title(5, '6. Final Check*')
    def tab_changed(change):
        nonlocal importstr, step1str, step2str, step3str, step4str, step5str, \
            range_chosen
        dfname = friendly_to_globalname[whichframe.value]
        if change['old'] == 0:
            # Update step 1 string
            step1str = '# Define data and trace name\\n'
            step1str += 'Xvals = '+dfname+'[\\"'
            step1str += str(Xcoord.value)+'\\"]\\n'
            step1str += 'Yvals = ' + dfname +'[\\"'
            step1str += str(Ycoord.value)+'\\"]\\n'
            step1str += 'tracename = \\"'+str(trace_name.value)+'\\"\\n\\n'
            pass
        if change['old'] == 1:
            # TODO need do something in case  tab is changed before a click
            # occurs outside a box that was just change. blur things will
            # require ipywidgets v8+
            # update step 2 string
            step2str = '# Define error (uncertainty)\\n'
            if yerrtype.value == 'none':
                step2str += 'Yerr = ' + dfname + '[\\"'
                step2str += str(Ycoord.value) + '\\"]*0 + 1\\n\\n'
            if yerrtype.value=='constant':
                step2str += 'Yerr = ' + dfname +'[\\"'
                step2str += str(Ycoord.value)+'\\"]*0 + ' + str(
                    yerrvalue.value) + '\\n\\n'
            if yerrtype.value == 'percent':
                step2str += 'Yerr = np.fabs('+ dfname +'[\\"'
                step2str += str(Ycoord.value)+'\\"])*0.01*' + str(
                    yerrvalue.value) + '\\n\\n'
            if yerrtype.value == 'data':
                step2str += 'Yerr = ' + dfname +'[\\"'
                step2str += str(yerrdata.value)+'\\"]\\n\\n'
            pass
        if change['old']== 2:
            # update step 3 string
            step3str = '# Define the fit model, initial guesses, and contraints\\n'
            step3str += 'fitmod = lmfit.models.'+str(modeldrop.value)+'()\\n'
            currmodel = getattr(models, str(modeldrop.value))()
            for k in params_set.children:
                param_name = str(k.children[0].value.split(':')[0])
                if param_name in currmodel.param_names:
                    step3str += 'fitmod.set_param_hint(\\"'+param_name+'\\",'
                    step3str += ' vary = '+str(not(k.children[1].children[
                        0].value))
                    temp_val = k.children[1].children[1].value
                    def tst_temp_val(temp_val):
                        if (temp_val != np.nan) and (temp_val != np.inf) and\
                                (temp_val != -np.inf) and (str(temp_val) != \
                                'nan'):
                            return True
                        else:
                            return False
                    if tst_temp_val(temp_val):
                        step3str += ', value = ' + str(temp_val)
                    temp_val = k.children[1].children[2].value
                    if tst_temp_val(temp_val):
                        step3str += ', min = ' + str(temp_val)
                    temp_val = k.children[1].children[3].value
                    if tst_temp_val(temp_val):
                        step3str += ', max = ' + str(temp_val)
                    step3str += ')\\n'
            step3str +='\\n'
            pass
        if change['new']>=4:
            # update ranges
            range_start = True
            ranges = []
            new_range = []
            if len(range_plot.data)>0:
                for i in range(len(range_plot.data[0].marker.color)):
                    if range_plot.data[0].marker.color[i] == range_plot_hilight:
                        new_range.append(i)
                        if not range_start:
                            ranges.append(new_range)
                            new_range = []
                        range_start = not range_start
            # update step 4 string
            covscalestr = 'False'
            if yerrtype.value == 'none':
                covscalestr = 'True'
            if len(ranges) > 0:
                range_chosen = True
                step4str = '# Define fit ranges\\n'
                step4str += 'Yfiterr = copy.deepcopy(Yerr) # ranges not to ' \
                            'fit = np.inf\\n'
                step4str += 'Xfitdata = copy.deepcopy(Xvals) # ranges where ' \
                            'fit not displayed = np.nan\\n'
                for i in range(len(ranges)):
                    if i == 0 and ranges[0][0]>0:
                        step4str += 'Yfiterr[0:'+str(ranges[0][0])+'] = ' \
                                                                   'np.inf\\n'
                        step4str += 'Xfitdata[0:'+str(ranges[0][0])+\
                                    '] = np.nan\\n'
                    if (i + 1) < len(ranges):
                        step4str += 'Yfiterr['+str(ranges[i][1]+1)+\
                                    ':'+str(ranges[i+1][0])+'] = np.inf\\n'
                        step4str += 'Xfitdata['+str(ranges[i][1]+1)+ \
                                    ':'+str(ranges[i+1][0])+'] = np.nan\\n'
                    if i+1 == len(ranges):
                        step4str += 'Yfiterr['+str(ranges[i][1]+1)+\
                                    ':'+str(len(range_plot.data[0].marker.
                                                color))+'] = np.inf\\n'
                        step4str += 'Xfitdata['+str(ranges[i][1]+1)+\
                                ':'+str(len(range_plot.data[0].marker.
                                            color))+'] = np.nan\\n'
                step4str += '\\n'
                step4str += '# Do fit\\n'
                step4str += str(fitname)+' = fitmod.fit(Yvals, x=Xvals, ' \
                    'weights = 1/Yfiterr, scale_covar = '+covscalestr+', ' \
                    'nan_policy = \\"omit\\")\\n\\n'
            else:
                range_chosen = False
                step4str = '# Do fit\\n'
                step4str += str(fitname)+' = fitmod.fit(Yvals, x=Xvals, ' \
                    'weights = 1/Yerr, scale_covar = '+covscalestr+', ' \
                    'nan_policy = \\"omit\\")\\n\\n'
            step4str += '# Calculate residuals (data - fit) because lmfit\\n'
            step4str += '#  does not calculate for all points under all ' \
                        'conditions\\n'
            step4str += 'resid = []\\n'
            step4str += 'for i in range(0,len('+str(fitname)+'.data)):\\n'
            step4str += '    resid.append('+str(fitname)+'.data[' \
                                        'i]-'+str(fitname)+'.best_fit[i])\\n\\n'
            pass
        if change['old'] == 4:
                # update step 5 string
                step5str = ''
                if range_chosen:
                    xstr = 'Xfitdata'
                    if not(extend_fit.value):
                        step5str += '# Delete residuals in ranges not fit\\n'
                        step5str += '# and fit values that are not ' \
                                    'displayed.\\n'
                        step5str += 'for i in range(len(resid)):\\n'
                        step5str += '    if np.isnan(Xfitdata[i]):\\n'
                        step5str += '        resid[i] = np.nan\\n'
                        step5str += '        '+str(fitname)+'.best_fit[i] = ' \
                                                   'np.nan\\n\\n'
                else:
                    xstr = 'Xvals'
                errbarstr = ''
                if yerrtype.value!='none':
                    errbarstr = ', error_y_type=\\"data\\", error_y_array=Yerr'
                xresidstr = xstr
                if extend_fit.value:
                    xresidstr = 'Xvals'
                mirrorstr = ''
                if mirror_axes.value:
                    mirrorstr = ', mirror = True'
                    if mirror_ticks.value:
                        mirrorstr = ', mirror = \\"ticks\\"'
                # the plot
                step5str += '# Plot Results\\n'
                step5str += str(figname) + ' = go.FigureWidget(' \
                                    'layout_template=\\"'+str(
                                    plot_template.value)+'\\")\\n'
                step5str += str(figname)+ '.update_layout(title = \\"'+ \
                                    str(plot_title.value)+'\\")\\n'
                step5str += str(figname) + '.set_subplots(rows=2, cols=1, ' \
                                           'row_heights=[0.2,0.8], ' \
                                           'shared_xaxes=True)\\n'
                step5str += 'scat = go.Scatter(y=resid,x='+xresidstr+', ' \
                                    'mode=\\"markers\\",' \
                                    'name = \\"residuals\\"'+errbarstr+')\\n'
                step5str += str(figname) + '.update_yaxes(title = ' \
                                        '\\"Residuals\\", ' \
                            'row=1, col=1, zeroline=True, zerolinecolor = ' \
                            '\\"lightgrey\\"'+str(mirrorstr)+')\\n'
                if mirror_axes.value:
                    step5str += str(figname) + '.update_xaxes(' \
                                           'row=1, col=1'+str(mirrorstr)+')\\n'
                step5str += str(figname) + '.add_trace(scat,col=1,row=1)\\n'
                step5str += 'scat = go.Scatter(x=Xvals, y=Yvals, ' \
                            'mode=\\"markers\\", name=tracename'+errbarstr+')\\n'
                step5str += str(figname) + '.add_trace(scat, col=1, ' \
                                           'row = 2)\\n'
                step5str += str(figname) + '.update_yaxes(title = ' \
                                           '\\"'+Y_label.value+'\\", ' \
                                           'row=2, col=1'+str(mirrorstr)+')\\n'
                step5str += str(figname) + '.update_xaxes(title = ' \
                                           '\\"'+X_label.value+'\\", ' \
                                           'row=2, col=1'+str(mirrorstr)+')\\n'
                if extend_fit.value:
                    step5str += 'scat = go.Scatter(y='+str(
                        fitname)+'.best_fit, x=Xvals, mode=\\"lines\\", '\
                                'line_color = \\"black\\", ' \
                                'name=\\"extrapolated\\",' \
                                 'line_dash=\\"dash\\")\\n'
                    step5str += str(figname) + '.add_trace(scat, col=1, ' \
                                               'row=2)\\n'
                step5str += 'scat = go.Scatter(y='+str(fitname)+'.best_fit,' \
                                    'x='+xstr+', mode=\\"lines\\", ' \
                                    'name=\\"fit\\", line_color = ' \
                                    '\\"black\\", line_dash=\\"solid\\")\\n'
                step5str += str(figname) + '.add_trace(scat,col=1,row=2)\\n'
                step5str += str(figname) + '.show()\\n\\n'
                pass
        if change['new'] == 3:
            df = friendly_to_object[whichframe.value]
            rangex = df[Xcoord.value]
            rangey = df[Ycoord.value]
            c =[]
            s = []
            if len(range_plot.data)> 0 and len(range_plot.data[
                0].marker.color) == len(range_plot.data[0]['x']):
                c = list(range_plot.data[0].marker.color)
                s = list(range_plot.data[0].marker.size)
            range_plot.data=[]
            range_plot.add_scatter(x=rangex,y=rangey, mode = 'markers',
                                   line_color = range_plot_line_color,
                                   marker_size = range_plot_marker_size)
            if len(range_plot.data[0]['x']) == len(c):
                with range_plot.batch_update():
                    range_plot.data[0].marker.color = c
                    range_plot.data[0].marker.size = s
            range_plot.data[0].on_click(update_range_point)
        if change['new'] ==5:
            if X_label.value == '' or Y_label.value == '':
                makeplot_notices.activate_notice(2)
                dofitbut.disabled = True
                dofitbut.button_style = ''
            else:
                makeplot_notices.deactivate_notice(2)
            if Xcoord.value == 'Choose X-coordinate.' or \
                    Ycoord.value == 'Choose X-coordinate.':
                makeplot_notices.activate_notice(0)
                dofitbut.disabled = True
                dofitbut.button_style = ''
            else:
                makeplot_notices.deactivate_notice(0)
            if modeldrop.value == '':
                makeplot_notices.activate_notice(1)
                dofitbut.disabled = True
                dofitbut.button_style = ''
            else:
                makeplot_notices.deactivate_notice(1)
            step6noticebox.value = makeplot_notices.notice_html()
        if len(makeplot_notices.get_active()) == 0:
            dofitbut.disabled = False
            dofitbut.button_style = 'success'
        # the best fit equation
        step6str = '# Display best fit equation\\n'
        step6str += fitresultstrs[modeldrop.value](fitname)
        JPSLUtils.select_containing_cell('pandasfitGUI')
        JPSLUtils.replace_text_of_next_cell(importstr + step1str + step2str +
                                     step3str + step4str + step5str + step6str)
        pass

    steps.observe(tab_changed, names = 'selected_index')
    display(steps)
    select_containing_cell('pandasfitGUI')
    new_cell_immediately_below()
    pass