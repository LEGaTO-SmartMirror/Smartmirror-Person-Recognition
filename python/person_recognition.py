import math
import random
import cv2
import json, sys 

def to_node(type, message):
	# convert to json and print (node helper will read from stdout)
	try:
		print(json.dumps({type: message}))
	except Exception:
		pass
	# stdout has to be flushed manually to prevent delays in the node helper communication
	sys.stdout.flush()

#Full HD image as default
IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920

try:
	to_node("status", "starting with config: " + sys.argv[1])
	config = json.loads(sys.argv[1])
	if 'image_height' in config:
		IMAGE_HEIGHT = int(config['image_height'])
	if 'image_width' in config:
		IMAGE_WIDTH = int(config['image_width'])
except:
	to_node("status", "starting without config as it was not readable/existent")	


def convertBack(x, y, w, h):
	x = x * IMAGE_WIDTH
	y = y * IMAGE_HEIGHT
	w = w * IMAGE_WIDTH
	h = h * IMAGE_HEIGHT
	xmin = int(round(x - (w / 2)))
	xmax = int(round(x + (w / 2)))
	ymin = int(round(y - (h / 2)))
	ymax = int(round(y + (h / 2)))
	return ((xmin, ymin),(xmax, ymax))

def to_node(type, message):
	# convert to json and print (node helper will read from stdout)
	try:
		print(json.dumps({type: message}))
	except Exception:
		pass
	# stdout has to be flushed manually to prevent delays in the node helper communication
	sys.stdout.flush()

# Result dict
person_dict = {}

# data structure
# {"DETECTED_OBJECTS": [{"TrackID": 1.0, "center": [0.12593, 0.7125], "name": "chair", "w_h": [0.2463, 0.15417]}, {"TrackID": 3.0, "center": [0.18889, 0.79167], "name": "bottle", "w_h": [0.10741, 0.1724]}]}

def contains(r1, r2):
	# return r1.x1 < r2.x1 < r2.x2 < r1.x2 and r1.y1 < r2.y1 < r2.y2 < r1.y2
	return r1[0][0] < r2[0][0] < r2[1][0] < r1[1][0] and r1[0][1] < r2[0][1] < r2[1][1] < r1[1][1]


to_node("status","Entering main loop")

while True:

	changed_values = False

	lines = sys.stdin.readline()
	data = json.loads(lines)
	if 'DETECTED_FACES' in data:
		dict_faces = data['DETECTED_FACES']
		#to_node("status", data['DETECTED_FACES'])
		for face in dict_faces:

			rect_face = convertBack(face["center"][0], face["center"][1], face["w_h"][0], face["w_h"][1] )

			for person in person_dict.keys():
				rect_person = convertBack(person_dict[person]["center"][0], person_dict[person]["center"][1], person_dict[person]["w_h"][0], person_dict[person]["w_h"][1])
				
				if contains(rect_person, rect_face):
					#to_node("status", "Found object person (ID " + str(person_dict[person]["TrackID"]) + ") that contains a face (ID " + str(face["TrackID"]))
					if "face" in person_dict[person]:
						if not (sorted(person_dict[person]["face"].items()) == sorted(face.items())) and face["confidence"] > 0.9:
							person_dict[person]["face"] = face.copy()
							changed_values = True
				
					else:
						person_dict[person]["face"] = face.copy()
						changed_values = True

		for person in person_dict.keys():
			if "face" in person_dict[person]:
				if not "center" in person_dict[person]["face"]:
					continue
				found = False
				for face in dict_faces:
					if (sorted(person_dict[person]["face"].items()) == sorted(face.items())):
						found = True
				if found is False:
					person_dict[person]["face"].pop("center")
					changed_values = True


	elif 'DETECTED_GESTURES' in data:
		dict_gestures = data['DETECTED_GESTURES']
		#to_node("status", data['DETECTED_GESTURES'])
	elif 'DETECTED_OBJECTS' in data:
		dict_objects = data['DETECTED_OBJECTS']
		#to_node("status", data['DETECTED_OBJECTS'])
		
		new_PersonDict = {}
		for element in dict_objects:
			if element["name"] == "person":
				if not element["TrackID"] in person_dict:
					new_PersonDict[element["TrackID"]] = element.copy()
					changed_values = True
					to_node("status", "new person was found")
				else: 
					new_PersonDict[element["TrackID"]] = person_dict[element["TrackID"]]
					if not new_PersonDict[element["TrackID"]]["center"] == element["center"]:
						new_PersonDict[element["TrackID"]]["center"] = element["center"]
						changed_values = True
					if not new_PersonDict[element["TrackID"]]["w_h"] == element["w_h"]:
						new_PersonDict[element["TrackID"]]["w_h"] = element["w_h"]
						changed_values = True
						
		if not (len(new_PersonDict) == len(person_dict)):
			changed_values = True
			
		person_dict = new_PersonDict
		
	if changed_values:
		to_node("RECOGNIZED_PERSONS", person_dict)