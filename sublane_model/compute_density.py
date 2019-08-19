import parse
import time
import random
import numpy as np

out_file = './out.xml'
net_file = './net.net.xml'

# with the out and net dictionary, compute the density dictionary(edges) 
def compute_func(out_file,net_file):
	buckets = 20
	(out,vehicleList) = parse.parse_out(out_file)
	net = parse.parse_net(net_file)

	edges = {}
	length = {}
	for k in net:
		edges[k] = {}
		length[k] = list(net[k].values())[0]

	# structure: edge id -> time -> buckets of vehicles

	for _, (t, es) in enumerate(out.items()):	
		for e in edges:
			edges[e][t] = []
			for i in range(buckets):
				edges[e][t].append(0)
		# i -- edge id, l -- we only care about vehicles inside
		for i, l in es.items():
			for v in l.values():
				for (loc, _) in v.values():
					idx = int(loc*buckets/length[i])
					if idx == len(edges[i][t]):
						idx -= 1
					edges[i][t][idx] += 1
	
	unused = []
	for e in edges:
		if max([max(x) for x in edges[e].values()]) == 0:
			unused.append(e)
	for e in unused:
		edges.pop(e)
		
	return (edges, length)
#end of compute_func

(edges,length) = compute_func(out_file,net_file)
#print(edges)