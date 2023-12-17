import numpy
import matplotlib.pyplot
import skrf
import cmath
from mpl_smithchart import SmithAxes

# NOTE: the material the wave is going into is 2 becaue it is *in-two*

epsilon0 = 8.854 * 10 ** -12 # permittivity of free space
mu0 = 4 * numpy.pi * 10 ** -7 # permeability of free space
eta0 = numpy.sqrt(mu0/epsilon0)
c = 1/numpy.sqrt(epsilon0*mu0)

def WaveImpedance(epsilon,mu):
    return numpy.sqrt(mu/epsilon)

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
    return complex(0,(phasevel/angfreq))

def AttenuationConstant(angfreq):
    return 0

def Gamma(PropCons,AttenCons):
    return PropCons + AttenCons

def dB(x):
    return 10*numpy.log(x)/numpy.log(10)

def Zin(zl,z0,gamma,l):
    # NOTE: this function uses the full form of the equations. make sure to append j when dealing with lossless lines
    return z0 * (zl + z0 * numpy.tanh(gamma*l))/(z0 + zl*numpy.tanh(gamma*l))

def Zl(zin,z0,gamma,l):
    return (z0*z0*numpy.tanh(gamma*l) - zin*z0)/(zin*numpy.tanh(gamma*l) - z0)

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

def CalcLength(z0,zin,zl,gamma):
    return numpy.arctanh((z0*zl - zin*z0)/(zin*zl - z0**2))/gamma

def CalcGamma(z0,zin,zl,length):
    return numpy.arctanh((z0&zl - zin*z0)/(zin*zl - z0**2))/length

class NetExt:
    def __init__(self,z0,f,data,datatype,name="GenNet",file=None):
        if datatype == "file":
            self.net=skrf.Network(file)
        elif datatype == "s":
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(z0=z0,frequency=freq,s=data,name=name)
        elif datatype == "z":
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(z0=z0,frequency=freq,z=data,name=name)
        elif datatype == "y":
            freq = skrf.Freqeuncy.from_f(f)
            self.net=skrf.Network(z0=z0,frequency=freq,y=data,name=name)
        self.resonantf()
        self.CrossoverF()
        return

    def resonantf(self):
        self.resf = self.net.f[numpy.argmin(abs(self.net.s[:,0,0]))]
        return

    def S11Min(self):
        return self.net.s[numpy.where(self.net.f==self.resf),0,0]

    def S21Res(self):
        return self.net.s[numpy.where(self.net.f==self.resf),1,0]

    def S21Min(self):
        fmin = self.net.f[numpy.argmin(abs(self.net.s[:,1,0]))]
        return fmin,self.net.s[numpy.where(self.net.f==fmin),1,0]

    def CrossoverF(self):
        diff = numpy.abs(numpy.abs(self.net.s[:,0,0]) - numpy.abs(self.net.s[:,1,0]))
        self.fcross = self.net.f[numpy.argmin(numpy.abs(diff))]
        # self.fcross = self.net.f[numpy.where(self.net.s[:,0,0] == self.net.s[:,1,0])]
        return

    def S21Cross(self):
        return self.net.s[numpy.where(self.net.f==self.fcross),1,0]

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

    def PlotS21Net(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(121)
        ax1.set_title(str(self.net.name) + " S21, Magnitude (dB)")
        ax1.plot(self.net.f, dB(numpy.abs(self.net.s[:,1,0])),label=("S21 Magnitude, " + str(self.net.name)))
        ax1.plot(self.resf,dB(numpy.abs(self.S21Res())),'X', markersize=10, label=("Resonance"))
        ax1.plot(self.S21Min()[0], dB(numpy.abs(self.S21Min()[1])),'+', markersize=10, label=("Minimum"))
        ax1.plot(self.fcross, dB(numpy.abs(self.S21Cross())), '*', markersize=10, label=("Crossover, S11"))
        ax1.legend()
        ax2=fig.add_subplot(122)
        ax2.set_title(str(self.net.name) + " S21, Phase (radians)")
        ax2.plot(self.net.f,numpy.angle(self.net.s[:,1,0]), label=("S21 Phase, " + str(self.net.name)))
        ax2.plot(self.resf,numpy.angle(self.S21Res()),'X', markersize=10, label=("Resonance"))
        ax2.plot(self.S21Min()[0], numpy.angle(self.S21Min()[1]),'+', markersize=10, label=("Minimum"))
        ax2.plot(self.fcross, numpy.angle(self.S21Cross()),'*', markersize=10, label=("Crossover, S11"))
        ax2.legend()
        fig.tight_layout
        matplotlib.pyplot.show(block=True)
        return

class TxLine:
    def __init__(self,z0,f,data,datatype,name="GenTxLine",file=None,KnownZl=None,length=None,gamma=None):
        self.determination = 0
        self.KnownZl = KnownZl
        self.length = length
        self.gamma = length
        self.dataype = datatype
        self.NetExt = NetExt(z0,f,data,datatype,name=name)
        if datatype != None:
            self.determination += 1
        if KnownZl != None:
            self.determination += 1
        if length != None:
            self.determination += 1
        if gamma != None:
            self.determination += 1
        return

class SpectrumTimeInfo:
    def __init__(self,data,type,orient):
        if orient == 1: self.data = data.T
        else: self.data = data
        self.type = str(type)
        self.Maxi()
        return
    def Plot(self):
        fig = matplotlib.pyplot.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.plot(self.data[0],self.data[1],label=("Power"))
        ax1.plot(self.data[0][numpy.where(self.maxi==self.data[0])],self.data[1][numpy.where(self.maxi==self.data[0])],'X', markersize=10,label=("Maximum"))
        ax1.set_title(str(self.type))
        ax1.legend()
        fig.tight_layout()
        matplotlib.pyplot.show(block=True)
        return
    def Maxi(self):
        self.maxi = self.data[0][numpy.argmax(self.data[1])]
        return

# TODO: add a filter network
# TODO: add a way to calculate stub values for impedance matching
# TODO: add specific kinds of transmission lines, such as coaxial, waveguide, microstrip,
