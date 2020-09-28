from flask import Flask
import os
from flask import request
import requests
import json
import base64
import cv2
import numpy as np
import json
import cv2
import time
import torch
from facenetModel import Facenet
from PIL import Image, ImageDraw
facenet = Facenet()
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
	return "Hello World!"

basedir = os.path.abspath(os.path.dirname(__file__))

# 傳遞圖片解碼
@app.route("/up_photo", methods=['GET', 'POST'])
def get_frame():
	start = time.time()
	
	frame = request.json["image"]
	frame=  json.loads(frame)
	frame = np.array(frame, dtype=np.uint8)

	framePil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
	features, boxes = facenet.predict(framePil)
	names = facenet.judge(features)

	# for i in range(len(boxes)):
	# 	cv2.rectangle(frame, (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][2]), int(boxes[i][3])), (0, 0, 255), 2)
	# 	cv2.putText(frame, names[i], ((int(boxes[i][0]), int(boxes[i][1]))), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)
	
	# cv2.imshow('frame', frame)
	#key_num = cv2.waitKey(1)

	#print("up_photo time :", time.time()-start)
	if(len(boxes) == 0):
		return json.dumps([names, []])
	else:
		return json.dumps([names, boxes.tolist()])

@app.route("/detect", methods=['GET', 'POST'])
def detect():
	start = time.time()
	
	frame = request.json["image"]
	frame=  json.loads(frame)
	frame = np.array(frame, dtype=np.uint8)

	framePil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
	boxes = facenet.detect(framePil)

	#print("detect time :", time.time()-start)
	if(type(boxes) == type(None)):
		return json.dumps([])
	else:
		return json.dumps(boxes.tolist())

@app.route("/judge", methods=['GET', 'POST'])
def judge():
	start = time.time()
	
	images = request.json["images"]
	images =  json.loads(images)
	images = torch.tensor(images).cuda().float()
	features = facenet.getFeatures(images)

	names = facenet.judge(features)

	#print("judge time :", time.time()-start)
	return json.dumps(names)


@app.route("/register", methods=['GET', 'POST'])
def register():
	start = time.time()
	image = request.json["image"]
	image =  json.loads(image)
	image = torch.tensor(image).cuda().float()
	feature = facenet.getFeatures(image)

	name = request.json["name"]
	if(type(name) == None):
		return "needName"


	#print("register time :", time.time()-start)
	facenet.register(feature, name)
	return "register success"
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8090)