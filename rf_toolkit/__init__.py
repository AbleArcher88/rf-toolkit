import numpy
import matplotlib.pyplot
import skrf
import cmath
from mpl_smithchart import SmithAxes

# TODO: Filter calculations

def RefractiveIndex():
    return

def TransmitAngle(thetai,n1,n2):
    return

def S11TE(eta1,eta2,thetai,thetat):
    # NOTE: eta1 is the impedance of the tx material, and eta2 is the impedance of the entering material
    return (eta2*numpy.cos(thetai) - eta1*numpy.cos(thetat))/(eta2*numpy.cos(thetai) + eta1*numpy.cos(thetat))

def S11TM(eta1,eta2,thetai,thetat):
    return (eta2*numpy.cos(thetat) - eta1*numpy.cos(thetai))/(eta2*numpy.cos(thetat) + eta1*numpy.cos(thetai))

def dB(x):
    return 10*numpy.log(x)/numpy.log(10)

def Zin(zl,z0,gamma,l):
    # NOTE: this function uses the full form of the equations. make sure to append j when dealing with lossless lines
    return z0 * (zl + z0 * numpy.tanh(gamma*l))/(z0 + zl*numpy.tanh(gamma*l))

def PlotSmithZ(z):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith')
    ax.plot(z,datatype=SmithAxes.Z_PARAMETER)
    return fig

def PlotSmithS(s):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith')
    ax.plot(s,datatype=SmithAxes.S_PARAMETER)
    return fig

def PlotSmithY(y):
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

# TODO: working on implementing a transmission line that can calculate Zin based on loads. hope to expand to calculate shunts

class TxLine:
    def __init__(z0,l):
        self.z0 = z0
        self.l = l
        return

class NetExt:
    def __init__(self,z0,file,f,data,datatype,name="GenNet"):
        if datatype == file:
            self.net=skrf.Network(file)
        elif datatype == s:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,s=s,name=name)
        elif datatype == z:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,z=z,name=name)
        elif datatype == y:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,y=y,name=name)
        self.resonantf()
        return

    def resonantf(self):
        self.resf = self.net.f[numpy.argmin(abs(self.net.s[:,0,0]))]
        return

    def S11Min(self):
        return self.net.s[numpy.where(self.net.f==self.resf),0,0]

    def PlotSmithZNet(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(111, projection='smith')
        ax1.set_title(str(self.net.name) + " Z, Smith Plot")
        ax1.plot(self.net.z[:,0,0], datatype=SmithAxes.Z_PARAMETER)
        ax1.plot(self.net.z[numpy.where(self.net.f==self.resf),0,0], marker='X', datatype=SmithAxes.Z_PARAMETER, markersize=10)
        fig.tight_layout()
        matplotlib.pyplot.show(block=True)
        return

    def PlotS11Net(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(121)
        ax1.set_title(str(self.net.name) + " S11, Magnitude (dB)")
        ax1.plot(self.net.f, dB(numpy.abs(self.net.s[:,0,0])))
        ax1.plot(self.resf,dB(numpy.abs(self.S11Min())),'X', markersize=10)
        ax2=fig.add_subplot(122)
        ax2.set_title(str(self.net.name) + " S11, Phase (radians)")
        ax2.plot(self.net.f,numpy.angle(self.net.s[:,0,0]))
        ax2.plot(self.resf,numpy.angle(self.S11Min()),'X', markersize=10)
        fig.tight_layout
        matplotlib.pyplot.show(block=True)
        return
