
import xml.etree.ElementTree as ET
import json

# convert Id to integer
def parse_route(file):
	tree = ET.parse(file)
	root = tree.getroot()
	vehicles = {}
	ref = {}
	num = -1
	for x in root:
		if x.tag == 'flow':
			vehicles[x.attrib['id']] = x.attrib['number']
	for x in vehicles:
		for i in range(int(vehicles[x])):
			num+=1
			if x[2]=="A":
				ref[str(x)+"."+str(i)] = (num,"AggrCar")
			elif x[2]=="C":
				ref[str(x)+"."+str(i)] = (num,"Car")
	return ref


def get_info(file):
	tree = ET.parse(file)
	root = tree.getroot()
	data = [None] * 500
	ref = parse_route(route)

	for time in root:
		t = int(float(time.attrib['time']))
		vehicles = {}
		for edge in time:
			for lane in edge:
				if lane.tag=='lane':
					for v in lane:
						Id = v.attrib['id']
						num = ref[Id][0]
						loc = float(v.attrib['pos'])
						typ = ref[Id][1]
						vehicles[num] = (loc,typ)
		if t < 500:
			data[t] = vehicles
	print(data)
	return data


if __name__ == "__main__":
	out = './out.xml'
	route = './input_routes.rou.xml'
	infoOut = './info_output.xml'

	f = open(infoOut, 'w')
	f.write(str(get_info(out)))	
	f.close()
