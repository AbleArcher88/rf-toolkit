import numpy
import matplotlib.pyplot
import skrf
import cmath
from mpl_smithchart import SmithAxes

def S11(zl,z0):
    return (zl - z0)/(zl + z0)

def dB(x):
    return 10*numpy.log(x)/numpy.log(10)

def Zin(zl,z0,beta,l):
    return z0 * (zl )

def PlotSmtithZ(z):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith')
    ax.plot(z,datatype=SmithAxes.Z_PARAMETER)
    return fig

def PlotSmtithS(s):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith')
    ax.plot(s,datatype=SmithAxes.S_PARAMETER)
    return fig

def PlotSmtithY(y):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith')
    ax.plot(y,datatype=SmithAxes.S_PARAMETER)
    return fig

def PlotS11db(f,s):
    fig = matplotlib.pyplot.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(f,dB(numpy.abs(s)))
    ax2 = fig.add_subplot(212)
    ax2.plot(f,numpy.angle(s))
    return fig

class NetExt:
    def __init__(z0,f,data,datatype,name="GenNet"):
        self.net=skrf.Network()
        self.resonantf()
        return

    def resonantf(self):
        self.resf = self.net.f[numpy.argmin(abs(net.s[:,0,0]))]
        return

    def S11Min(self):
        return self.net.s[numpy.where(self.net.f==resf),0,0]

    def PlotSmithNetZ(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(111, projection='smith')
        ax1.plot(self.net.z[:,0,0], datatype=SmithAxes.Z_PARAMETER)
        ax1.plot(self.net.z[numpy.where(self.net.f==resf),0,0], marker='X', datatype=SmithAxes.Z_PARAMETER, markersize=10)
        fig.tight_layout()
        matplotlib.pyplot.show(block=True)
        return

    def PlotS11NetZ(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(121)
        ax1.set_title("S11, Magnitude (dB)")
        ax1.plot(self.net.f, dB(numpy.abs(self.net.s[:,0,0])))
        ax1.plot(resf,dB(numpy.abs(S11Min(self.net,resf))),'X', markersize=10)
        ax2=fig.add_subplot(122)
        ax2.set_title("S11, Phase (radians)")
        ax2.plot(self.net.f,numpy.angle(self.net.s[:,0,0]))
        ax2.plot(resf,numpy.angle(S11Min(self.net,resf)),'X', markersize=10)
        fig.tight_layout
        matplotlib.pyplot.show(block=True)
        return
