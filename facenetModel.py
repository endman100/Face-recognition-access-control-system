import torch
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from torchvision import transforms
import cv2
import numpy as np
import mmcv
import os
from tqdm import tqdm

from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#workers = 0 if os.name == 'nt' else 4
class Facenet(object):
	def __init__(self):
		super(Facenet, self).__init__()
		self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
		print('Running on device: {}'.format(self.device))
		self.mtcnn = MTCNN(
						image_size=160, margin=20, min_face_size=20,
						thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
						device=self.device
					 ).eval()
		self.resnet = InceptionResnetV1(pretrained='vggface2', device=self.device).eval().to(self.device)
		self.loader = transforms.Compose([transforms.ToTensor()]) 
		self.featureLib = []
		self.featureLibName = []
	def boxToImg(self, img, boxes, prob):
		returnImg = []
		if(type(boxes) == type(None)):
			return []
		for i in range(len(boxes)):
			if(prob[i] > 0.5):
				temp = self.loader(img.crop(boxes[i]).resize((160, 160)))
				returnImg.append(temp)
			else:
				print("prob < 0.3")
		return torch.stack(returnImg).to(self.device)
	def predict(self, img):
		#img = self.loader(img)
		# print(img.size)
		#img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		boxes, prob = self.mtcnn.detect(img)
		imgs = self.boxToImg(img, boxes, prob)
		if(type(imgs) == list):
			return [], []
		embeddings = self.resnet(imgs).detach()
		return embeddings, boxes
	def detect(self, img):
		boxes, prob = self.mtcnn.detect(img)
		return boxes
	def getFeatures(self, imgs):
		features = self.resnet(imgs).detach()
		return features
	def register(self, newFeature, name):
		self.featureLib.append(newFeature)
		self.featureLibName.append(name)
		print("register : ", name)
	def judge(self, newFeature):
		if(len(newFeature) == 0):
			return []
		if(len(self.featureLib) == 0):
			retrunList = []
			for i in range(len(newFeature)):
				retrunList.append("notRegister")
			return retrunList
		dists = [[(e1 - e2).norm().item() for e2 in self.featureLib] for e1 in newFeature]
		temp = np.argmin(dists, axis=1)
		# for i in range(len(dists)):
		# 	print(dists[i], i)
		# 	print(self.featureLibName)
		names = []
		for i in range(len(temp)):
			print(dists[i][temp[i]], self.featureLibName[temp[i]])
			if(dists[i][temp[i]] > 0.25):
				names.append("notRegister")
			else:
				names.append(self.featureLibName[temp[i]])
		#print(names)
		return names



if __name__ == '__main__':
	facenet = Facenet()
	img = Image.open("20190826081359546 .jpg") 
	for i in tqdm(range(100000)):
		facenet.predict(img)
	