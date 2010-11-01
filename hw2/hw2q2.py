# Daren Hasenkamp
# 19362801

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.mlab as ml
import numpy as np
import sys
import pylab as pl

img = mpimg.imread(sys.argv[1])
fsimg = np.fft.fft2(img)
powerspectrum = np.absolute(fsimg)
p = ml.prctile(powerspectrum.flatten(),p=(95,99.983))
l1 = len(fsimg)
l2 = len(fsimg[0])
fsimg2 = fsimg.copy()
fsimg[:,50:-50] = 0
fsimg[50:-50,:] = 0
for i in range(0,l1) :
	for j in range(0,l2) :
		if powerspectrum[i][j] > p[1] :
			fsimg2[i][j] = 0

for i in range(0,l1) :
	for j in range(0,l2) :
		if powerspectrum[i][j] > p[0] :
			powerspectrum[i][j] = 0

cutpowerspectrum = np.absolute(fsimg)
for i in range(0,l1) :
	for j in range(0,l2) :
		if cutpowerspectrum[i][j] > p[0] :
			cutpowerspectrum[i][j] = 0

ifsimg = np.fft.ifft2(fsimg)
ifsimg = np.abs(ifsimg)
plt.figure(1)
imgplot = plt.imshow(ifsimg.astype(float))
imgplot.set_cmap("Greys")
plt.figure(2)
imgplot = plt.imshow(img)
imgplot.set_cmap("Greys")
plt.figure(3)
imgplot = plt.imshow(powerspectrum.astype(float))
imgplot.set_cmap("Blues")
plt.figure(4)
imgplot = plt.imshow(cutpowerspectrum.astype(float))
imgplot.set_cmap("Blues")
plt.figure(5)
imgplot = plt.imshow(np.fft.ifft2(fsimg2).real.astype(float))
imgplot.set_cmap("Greys")
plt.show()
