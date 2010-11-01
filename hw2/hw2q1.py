# Daren Hasenkamp
# 19362801

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splrep
from scipy.optimize import leastsq

e = 2.718281828
samplepoints = 500

def model(x,p) :
	return p[0] * e**(p[1]*x) + p[2]
def residuals(p,y,x) :
	return y - model(x,p)

xvals = np.linspace(0,4,samplepoints)
yvals = (2.0 * e**(-.75*xvals) + .1)
nyvals = yvals + np.random.normal(scale=.1,size=samplepoints)

p0 = [2.0,-.75,.1]
plsq = leastsq(residuals,p0,args=(nyvals,xvals))

lsvals = model(xvals,plsq[0])

nydeg0ls = np.polyval(np.polyfit(xvals,nyvals,0),xvals)
nydeg1ls = np.polyval(np.polyfit(xvals,nyvals,1),xvals)
nydeg2ls = np.polyval(np.polyfit(xvals,nyvals,2),xvals)
nydeg3ls = np.polyval(np.polyfit(xvals,nyvals,3),xvals)
nydeg1sp = splrep(xvals,nyvals,k=1)
nydeg2sp = splrep(xvals,nyvals,k=2)
nydeg3sp = splrep(xvals,nyvals,k=3)

plt.figure(1)
plt.plot(xvals,nyvals,xvals,nydeg1ls,nydeg1sp[0],nydeg1sp[1])
plt.figure(2)
plt.plot(xvals,nyvals,xvals,nydeg2ls,nydeg2sp[0],nydeg2sp[1])
plt.figure(3)
plt.plot(xvals,nyvals,xvals,nydeg3ls,nydeg3sp[0],nydeg3sp[1])
plt.figure(4)
plt.plot(xvals,nyvals,xvals,lsvals,xvals,yvals,xvals,nydeg0ls)
plt.show()



