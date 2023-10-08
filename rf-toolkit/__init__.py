import numpy
import matplotlib.pyplot
import skrf
import cmath
from mpl_smithchart import SmithAxes

def S11(zl,z0):
    return (zl - z0)/(zl - z0)
