
import xml.etree.ElementTree as ET
import json

# return the type of each vehicle
def parse_route(file):
	tree = ET.parse(file)
	root = tree.getroot()
	vehicles = {}
	for x in root:
		if x.tag == 'vehicle':
			vehicles[x.attrib['id']] = x.attrib['type']
	return vehicles

def get_info(file):
	tree = ET.parse(file)
	root = tree.getroot()
	data = [None] * 250
	typeList = parse_route(route)

	for time in root:
		t = int(float(time.attrib['time']))
		vehicles = {}
		for edge in time:
			for lane in edge:
				if lane.tag=='lane':
					for v in lane:
						Id = v.attrib['id']
						num = int(Id)
						loc = float(v.attrib['pos'])
						typ = typeList[Id]
						vehicles[num] = (loc,typ)
		if t < 500:
			data[int(t/2)] = vehicles
		
	return data


if __name__ == "__main__":
	out = './out.xml'
	route = './input_routes.rou.xml'
	infoOut = './info_output.xml'

	f = open(infoOut, 'w')
	f.write(str(get_info(out)))	
	f.close()
