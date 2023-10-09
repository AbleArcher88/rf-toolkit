import numpy
import matplotlib.pyplot
import skrf
import cmath
from mpl_smithchart import SmithAxes

# TODO: Filter calculations

# NOTE: the material the wave is going into is 2 becaue it is *in-two*

epsilon0 = 8.854 * 10 ** -12 # permittivity of free space
mu0 = 4 * numpy.pi * 10 ** -7 # permeability of free space
eta0 = numpy.sqrt(mu0/epsilon0)
c = 1/numpy.sqrt(epsilon0*mu0)

def WaveImpedance(epsilon,mu):
    return sqrt(mu/epsilon)

def RefractiveIndex(eta):
    return eta0/eta

def TransmitAngle(thetai,n1,n2):
    return numpy.arcsin(n1*numpy.sin(thetai)/n2)

def S11TE(eta1,eta2,thetai,thetat):
    # NOTE: eta1 is the impedance of the tx material, and eta2 is the impedance of the entering material
    return (eta2*numpy.cos(thetai) - eta1*numpy.cos(thetat))/(eta2*numpy.cos(thetai) + eta1*numpy.cos(thetat))

def S11TM(eta1,eta2,thetai,thetat):
    return (eta2*numpy.cos(thetat) - eta1*numpy.cos(thetai))/(eta2*numpy.cos(thetat) + eta1*numpy.cos(thetai))

def S11TEM(z0,zl):
    return S11TE(z0,zl,0,0)

def PhaseVelocity(n):
    return c/n

def PropagationConstant(phasevel,angfreq):
    return j*(phasevel/angfreq)

def AttenuationConstant(angfreq):
    return 0

def Gamma(PropCons,AttenCons):
    return PropCons + AttenCons

def dB(x):
    return 10*numpy.log(x)/numpy.log(10)

def Zin(zl,z0,gamma,l):
    # NOTE: this function uses the full form of the equations. make sure to append j when dealing with lossless lines
    return z0 * (zl + z0 * numpy.tanh(gamma*l))/(z0 + zl*numpy.tanh(gamma*l))

def PlotSmithZ(z,z0=50):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith', axes_impedance=z0)
    ax.plot(z,datatype=SmithAxes.Z_PARAMETER)
    return fig

def PlotSmithS(s,z0=50):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith', axes_impedance=z0)
    ax.plot(s,datatype=SmithAxes.S_PARAMETER)
    return fig

def PlotSmithY(y,z0=50):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111, projection='smith', axes_impedance=z0)
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
    def __init__(self,z0,length,load,freq):
        self.z0 = z0
        self.length = length
        self.load = load
        self.freq = freq
        return
    def TxGamma(self):
        phasevel = PhaseVelocity(RefractiveIndex(self.z0))
        self.gamma = Gamma(PropagationConstant(phasevel,2*numpy.pi*self.freq),AttenuationConstant(2*numpy.pi*self.freq))
        return
    def S11in(self):
        return S11TEM(self.z0,self.load)*numpy.exp(-2*self.gamma*self.length)
    def ZinLine(self):
        return Zin(self.load,self.z0,self,self.gamma,self.length)

    
class NetExt:
    def __init__(self,z0,f,data,datatype,name="GenNet",file=None):
        if datatype == "file":
            self.net=skrf.Network(file)
        elif datatype == s:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,s=data,name=name)
        elif datatype == z:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,z=data,name=name)
        elif datatype == y:
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(frequency=freq,y=data,name=name)
        self.resonantf()
        return

    def resonantf(self):
        self.resf = self.net.f[numpy.argmin(abs(self.net.s[:,0,0]))]
        return

    def S11Min(self):
        return self.net.s[numpy.where(self.net.f==self.resf),0,0]

    def PlotSmithZNet(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(111, projection='smith', axes_impedance=self.net.z0[0,0])
        ax1.set_title(str(self.net.name) + " Z, Smith Plot")
        ax1.plot(self.net.z[:,0,0], datatype=SmithAxes.Z_PARAMETER, label=("Z, " + str(self.net.name)))
        ax1.plot(self.net.z[numpy.where(self.net.f==self.resf),0,0], marker='X', datatype=SmithAxes.Z_PARAMETER, markersize=10,label="Resonance")
        ax1.legend()
        fig.tight_layout()
        matplotlib.pyplot.show(block=True)
        return

    def PlotS11Net(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(121)
        ax1.set_title(str(self.net.name) + " S11, Magnitude (dB)")
        ax1.plot(self.net.f, dB(numpy.abs(self.net.s[:,0,0])),label=("S11 Magnitude, " + str(self.net.name)))
        ax1.plot(self.resf,dB(numpy.abs(self.S11Min())),'X', markersize=10, label=("Resonance"))
        ax1.legend()
        ax2=fig.add_subplot(122)
        ax2.set_title(str(self.net.name) + " S11, Phase (radians)")
        ax2.plot(self.net.f,numpy.angle(self.net.s[:,0,0]), label=("S11 Phase, " + str(self.net.name)))
        ax2.plot(self.resf,numpy.angle(self.S11Min()),'X', markersize=10, label=("Resonance"))
        ax2.legend()
        fig.tight_layout
        matplotlib.pyplot.show(block=True)
        return
