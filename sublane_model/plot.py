import compute_density
import matplotlib.pyplot as plt
import time
import random
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline


out_file = './out.xml'
net_file = './net.net.xml'

(edges,length) = compute_density.compute_func(out_file,net_file)
buckets = 20

# plot the desity profile
for e, data in edges.items():

	chunk = length[e]/buckets

	xdata = np.linspace(0, length[e], buckets)
	X = np.linspace(0, length[e], int(length[e]) * 10)

	plt.figure(e)
	axes = plt.gca()
	y_upper = max([max(y) for y in data.values()])
	y_lower = -(y_upper/5)

	for i, t in data.items():
		ydata = np.array(t)
		spl = make_interp_spline(xdata, ydata, k=3)
		Y = spl(X)

		axes.set_ylim(y_lower, y_upper+2)

		line, = axes.plot(X, Y, 'r-')
		axes.plot(xdata, ydata, 'bo')
	
		plt.title(e)
		plt.draw()
		plt.pause(1e-17)
		time.sleep(0.3)
		plt.cla()
plt.show()
