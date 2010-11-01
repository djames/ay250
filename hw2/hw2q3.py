# Daren Hasenkamp
# 19362801

import numpy as np

def my_matrixinv(x) :
	x = x.copy() # Do things non-destructively
	x = x.astype(float)
	if len(x) != len(x[0]) : return None
	if np.linalg.det(x) == 0.0 : return None
	xi = np.zeros([len(x),len(x)])
	for m in range(0,len(x)) :
		xi[m][m] = 1.0
	for i in range(0,len(x)) :
		xi[i] = xi[i] / x[i][i]
		x[i] = x[i] / x[i][i]
		for j in range(0,len(x)) :
			if j != i:
				xi[j] = xi[j] - ((x[j][i]/x[i][i])*xi[i])
				x[j] = x[j] - ((x[j][i]/x[i][i])*x[i])
	return xi
