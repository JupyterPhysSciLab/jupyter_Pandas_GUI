def get_ipython_globals():
    """
    This operation returns the dictionary of global objects in the
    interactive namespace.
    :return: dict that is equivalent to an interactive call to Globals().
    """
    import inspect
    is_not_ipython_global = True
    frame = inspect.currentframe()
    global_dict = frame.f_globals
    try:
        namestr = global_dict['__name__']
        docstr = global_dict['__doc__']
        # print(global_dict['__name__'])
        # print(docstr)
    except KeyError:
        namestr = ''
    if (namestr == '__main__'):
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
                print(str(namestr) + ': ' + str(docstr))
                # print(global_dict['__name__'])
            except KeyError:
                namestr = ''
            if (namestr == '__main__'):
                is_not_ipython_global = False
    except AttributeError:
        raise AttributeError(
            'Unable to find `__main__` of interactive session. Are you ' \
            'running in Jupyter or IPython?')
    return (global_dict)

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
    dataframenames = []
    global_dict = get_ipython_globals()
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
            dataframenames.append(k)
    return dataframenames
