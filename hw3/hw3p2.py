# Daren Hasenkamp
# 19362801

import numpy as np
import matplotlib.mlab as ml
import matplotlib.pyplot as plt
import aifc, sys

# First, build a one-to-one mapping between notes and their frequencies.
notes = []
for i in range(0,9):
	notes += map(lambda x: x+str(i),["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])
frequencies= [16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01, 4434.92, 4698.64, 4978.03]

# My aifc library complained about these chunktypes; it doesn't seem to affect my
# ability to produce proper results just to ignore them.
aifc._skiplist += ('CHAN',)
aifc._skiplist += ('LGWV',)

# f is a single frame(4 bytes) of audio, returns a length 2
# list containing both channels' integer representations
def parseframe(f) :
	s1 = (ord(f[0])<<8)|ord(f[1])
	s2 = (ord(f[2])<<8)|ord(f[3])
	return [s1,s2]

def main(fname) :
	audiofile = aifc.open(fname)
	# first few frames looked like junk to me, skip 'em
	audiofile.readframes(10)
	# Read 1 seconds worth of frames so that when we move to fourier space, indices
	# in our array correspond to frequencies
	f = audiofile.readframes(audiofile.getframerate())
	# create 2 arrays of the samples from each channel
	chan0 = []
	chan1 = []
	while len(f) > 0 :
		a = parseframe(f[:4])
		chan0.append(a[0])
		chan1.append(a[1])
		f = f[4:]
	# take fft, get power and mean/standard deviation of power
	chan0fft = np.fft.fft(chan0)
	chan0power = np.absolute(chan0fft)
	mean = np.mean(chan0power)
	std = np.std(chan0power)

	
	tol = 5
	dist = 5
	print "Notes present in "+fname+": ",
	# Now check whether each musical note frequency is present in the
	# power spectrum
	for n,freq in enumerate(frequencies) :
		# (Note that the indices of chan0power are exactly the frequencies
		# they represent, since chan0power was generated from exactly
		# one second's worth of sound.)
		# round frequency to nearest integer
		freq = int(round(freq))
		# get power at freq
		presence = chan0power[freq]
		# add in power around frequency
		for i in range(1,dist+1) :
			presence += chan0power[freq+i] + chan0power[freq-i]
		# average the power
		presence /= ((dist*2)+1)
		# if the power is significantly larger than the mean, it means
		# a note is being played at this frequency
		if (presence - mean)/std > tol :
			print notes[n],
			# Now cut out a small range around each integer multiple of freq
			for i in range(1, 30) :
				chan0power[i*freq] = 0
				for j in range(1, dist+10) :
					chan0power[i*freq + j] = 0
					chan0power[i*freq - j] = 0
	print

# run everything
for i in range(1,10) :
	main("sound_files/"+str(i)+".aif")
