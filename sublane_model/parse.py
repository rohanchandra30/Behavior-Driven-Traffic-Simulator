import xml.etree.ElementTree as ET
import json

def parse_out(file):
	tree = ET.parse(file)
	root = tree.getroot()
	data = {}
	vehicleList = set()
	
	for time in root:
		t = int(float(time.attrib['time']))
		traf = {}
		for edge in time:
			# edge -- attrib: edge id
			lanes = {}
			for lane in edge:
				# lane -- attrib: lane id
				if lane.tag=='lane':
					vehicles = {}
					for v in lane:
						num = v.attrib['id']
						loc = float(v.attrib['pos'])
						speed = float(v.attrib['speed'])
						vehicles[num] = (loc, speed)
						vehicleList.add(num)
					lanes[lane.attrib['id']] = vehicles
			traf[edge.attrib['id']] = lanes
		data[t] = traf
	return (data,vehicleList)

def parse_net(file):
	data = {}
	tree = ET.parse(file)
	root = tree.getroot()

	for e in [x for x in root if x.tag == 'edge' and not ':' in x.attrib['id']]:
		lanes = {}
		for ls in e:
			lanes[ls.attrib['id']] = float(ls.attrib['length'])
		data[e.attrib['id']] = lanes
	return data


if __name__ == "__main__":
	out = './out.xml'
	net = './net.net.xml'
	result = './result.dict'

	info = {}
	info['out'] = parse_out(out)
	info['net'] = parse_net(net)

	f = open(result, 'w')
	f.write(str(info))	
	f.close()