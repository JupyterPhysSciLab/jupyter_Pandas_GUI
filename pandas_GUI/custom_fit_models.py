from lmfit import model
from lmfit.models import update_param_vals, Model

####
# Functions
####
def offsetexp(x, x_o, y_o, A, tau):
    """
    This returns an exponetial approach to y0 with a decay rate of
    tau. x0 is the start of the exponential approach and A is
    the negative of the change from the value at x = x offset and x = oo.
    :param x: independent variable
    :param x0: the effective time zero for the function
    :param y0: the value of the function at x = oo
    :param A: the negative of the total change between x = x0
    and x = oo
    :param tau: the decay lifetime
    :return: y0 + A*exp(-(x-x0)/tau)
    """
    from numpy import exp
    return y_o + A*exp(-(x-x_o)/tau)

####
# Models
####

class OffsetExpModel(Model):
    def __init__(self, independent_vars=['x'], prefix='', nan_policy='raise',
                 **kwargs):
        kwargs.update({'prefix': prefix, 'nan_policy': nan_policy,
                       'independent_vars': independent_vars})
        super().__init__(offsetexp, **kwargs)

    def guess(self, data, x, **kwargs):
        """Estimate initial model parameter values from data."""
        from numpy import argmax, argmin
        B = data[len(data)-1]
        maxloc = argmax(data)
        minloc = argmin(data)
        maxdiffloc = maxloc
        A = data[maxloc] - B
        x0 = x[maxloc]
        maxdiff = abs(B - data[maxloc])
        if abs(B - data[minloc]) > maxdiff:
            A = data[minloc] - B
            x0 = x[minloc]
        decay_interval = x[len(x)-1] - x0
        pars = self.make_params(A=A, x_o = x0, y_o = B,
                                tau = decay_interval/3)
        return update_param_vals(pars, self.prefix, **kwargs)

    @property
    def expr(self):
        return 'y_o + A*exp(-(x-x_o)/tau)'
