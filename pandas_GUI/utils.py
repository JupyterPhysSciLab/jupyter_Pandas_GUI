""" pandas_GUI.utils
The Jupyter JS call utils below are being deprecated by utilites in the
package JPSLUtils (https://github.com/JupyterPhysSciLab/JPSLUtils).
"""
import ipywidgets

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

def replace_text_of_current_cell(text):
    from IPython.display import display, HTML
    from IPython.display import Javascript as JS
    display(JS('Jupyter.notebook.get_selected_cell().set_text("' + text +'");'))


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

######
# Pandas and Figures routines
######

def find_pandas_dataframe_names():
    """
    This operation will search the interactive name space for pandas
    DataFrame objects. It will not find DataFrames that are children
    of objects in the interactive namespace. You will need to provide
    your own operation for finding those.

    :return list: string names for objects in the global interactive
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
    """
    This operation will search the interactive namespace for objects that are
    plotly Figures (plotly.graph_objects.Figure) or plotly FigureWidgets
    (plotly.graph_objects.FigureWidget). It will not find Figures or
    FigureWidgets that are children of other objects. You will need to
    provide your own operation for finding those.

    :return list: of string names for the objects in the global
    interactive namespace that are plotly Figures or FigureWidgets.
    """
    from plotly.graph_objects import Figure, FigureWidget
    from IPython import get_ipython

    fignames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k],
                                                       (Figure,FigureWidget)):
            fignames.append(k)
    return fignames

def find_fit_names():
    """
    This operation will search the interactive namespace for objects that are
    lmfit results (lmfit.model.ModelResults). It will not find fit results
    that are children of other objects. You will need to
    provide your own operation for finding those.

    :return list: of string names for the objects in the global
    interactive namespace that are lmfit fit results.
    """
    from lmfit.model import ModelResult
    from IPython import get_ipython

    fitnames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k],
                                                       ModelResult):
            fitnames.append(k)
    return fitnames

class iconselector():
    """
    This class provides a self updating set of small buttons showing the
    font-awesome icons passed to it. The user selected icon is highlighted
    in darkgray. The `selected` attribute (value is a synonym) is set to the
    name of the current selection. The `box` attribute is an ipywidget HBox
    that can be displayed or incorporated into more complex ipywidget
    constructs to interact with the user.
    """
    #####
    # TODO: add .observe option to icon selector...change object to extend
    # the appropriate widget type?
    #####
    def __init__(self,iconlist, selected = None):
        """

        :param list iconlist: list of string names for the font awsome icons to
        display. The names should not be prefixed with 'fa-'.

        :param string selected: name of selected icon (default = None).
        """
        from ipywidgets import HBox, Button, Layout
        self.buttons = []
        self.selected = selected # This will be the selected icon name

        def iconbutclk(but):
            self.selected = but.icon
            for k in self.buttons:
                if k.icon != self.selected:
                    k.style.button_color = 'white'
                else:
                    k.style.button_color = 'darkgray'
            pass

        smallbut = Layout(width='30px')
        for k in iconlist:
            tempbut = Button(icon=k,layout=smallbut)
            tempbut.style.button_color = 'white'
            tempbut.style.boarder = 'none'
            tempbut.on_click(iconbutclk)
            self.buttons.append(tempbut)
        if self.selected != None:
            for k in self.buttons:
                if k.icon == self.selected:
                    iconbutclk(k)
        self.box = HBox(self.buttons) # This can be passed as a widget.

    @property
    def value(self):
        return self.selected

class notice_group():
    """
    A notice group contains a list of strings that are referred to by their
    index. The group keeps track of which notices are 'active'. A call to the
    `.notice_html()` method returns an unordered html formatted list of the
    notice texts. This can be used to display or update notice text
    for the user.

    Optional notice group color, header and footers can be provided.
    """
    def __init__(self, noticelist, header='', footer = '', color = ''):
        """

        :param list noticelist: list of strings of the text for each notice

        :param string header: string providing a header for this notice group

        :param string footer: string providing a footer for this notice group

        :param string color: string compatible with css color attribute,
        used to color the displayed notices. The color not impact headers
        and footers.
        """
        self.header = header
        self.noticelist = noticelist
        self.footer = footer
        self.color = color
        self.active = []

    def get_active(self):
        """Returns a list of indexes of active notices"""
        return self.active

    def set_active(self,whichnotices):
        """
        Used to set a specific list of notices to active. This will remove
        active notices that are not in the provided list.

        :param  list whichnotices:
        """
        self.active = whichnotices
        pass

    def activate_notice(self, notice_id):
        """
        adds one of the notices to the active list

        :param int notice_id:
        """
        if notice_id not in self.active:
            self.active.append(notice_id)
        pass

    def deactivate_notice(self, notice_id):
        """
        removes a notice from the active list

        :param int notice_id:
        """
        if notice_id in self.active:
            self.active.remove(notice_id)
        pass

    def notice_html(self):
        """
        Provides an html formatted string displaying the active notices.

        :return string: string of html.
        """
        notice_header = ''
        if self.header !='':
            notice_header = '<h4 style="text-align:center;">'+self.header+\
                            ' </h4><ul>'
        notice_footer = self.footer+'</ul>'
        notice_txt = notice_header
        itemstart = '<li style="color:'+self.color+';">'
        for j in self.active:
            notice_txt += itemstart + self.noticelist[j]+'</li>'
        notice_txt += notice_footer
        return notice_txt

class build_run_snip_widget(ipywidgets.GridBox):

    def __init__(self, defaulttxt, output_elem):
        """
        Defines a widget that runs code built in it and replaces itself with
        the results.
        :param defaulttxt: Initial text in the codebox
        :param output_elem: Where this element will be located (an ipywidget
        `Output()` element). Must be created before creating this object.
        """
        from ipywidgets import Textarea, Layout, Button, VBox, GridBox
        from ipywidgets import HTML as richLabel
        from IPython.display import display, HTML, clear_output
        from IPython import get_ipython
        self.run_env = (get_ipython().user_ns["JPSLUtils"]).notebookenv
        self.sniptext = Textarea(
            layout=Layout(width='98%', height='200px'),
            value=defaulttxt
        )
        self.value = self.sniptext.value
        self.dobutton = Button(description='Run Code')
        instr_str = '<div style="line-height:1;">'
        if self.run_env == 'colab':
            instr_str += \
            '<p>You appear to be running in Google Colabratory. When done ' \
            'working through all the steps, copy the code at left into a ' \
            'new code cell to run it. In Jupyter lab and classic Jupyter ' \
            'notebooks this can be done automatically for you.</p>'
        else:
            instr_str += \
            '<p>You appear to be running in Jupyter lab. When done ' \
            'working through all the steps, clicking on the "Run Code" ' \
            'button will replace the GUI with the results of running the ' \
            'code. Copying the code in the collapsed "Code that was run" ' \
            'summary into a code cell will prevent the code from being ' \
            'lost if outputs are cleared.</p>'
        instr_str += '<br/><p>POWER USER HINT: You can repeatedly try ' \
                     'different settings by copying the completed code from ' \
                     'the text box at left into a code cell. Then run it. ' \
                     'Then use the GUI tools to update the code at left and ' \
                     'try again.</p></div>'
        self.instructions = richLabel(value = instr_str)
        if self.run_env == 'colab':
            self.dobox = VBox([self.instructions])
        else:
            self.dobox = VBox([self.dobutton,self.instructions])
        def onRunCode(change):
            from IPython import get_ipython
            shell = get_ipython()
            output_elem.clear_output()
            with output_elem:
                display(HTML(
                '<details><summary style="cursor:pointer;"><span style="font-weight:bold;"><a>' \
                'Code that was run</a></span>(click to toggle visibility)</summary>' \
                '<div style="background:#eff0f1;white-space:pre-line;white-space:pre-wrap;">' \
                '<code><xmp>' + self.sniptext.value
                +'</xmp></code></div></details>'))
                display(HTML('<h3>Result<h3>'))
                exec(str(self.sniptext.value), shell.user_ns)
            pass

        self.dobutton.on_click(onRunCode)

        super(build_run_snip_widget, self).__init__([self.sniptext,
                                             self.dobox],
                                            layout=Layout(
            grid_template_rows='auto',
            grid_template_columns='75% 25%',
            grid_template_areas="self.sniptext self.dobox"))