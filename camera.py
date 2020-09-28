import cv2
from facenetModel import Facenet
from PIL import Image, ImageDraw

facenet = Facenet()
# 選擇第二隻攝影機
cap = cv2.VideoCapture(0)
registerName = "joe"
while(True):
	# 從攝影機擷取一張影像
	ret, frame = cap.read()

	framePil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
	features, boxes = facenet.predict(framePil)




	key_num = cv2.waitKey(1)
	#print(key_num)
	if(key_num == 42):
		registerName = input()
	if(key_num == 43):
		maxBox = -1
		maxNum = -1
		for i in range(len(boxes)):
			temp = abs(boxes[i][0]-boxes[i][2]) * abs(boxes[i][1]-boxes[i][3])
			if(temp > maxNum):
				maxNum = temp
				maxBox = i
		if(maxBox != -1):
			facenet.register(features[maxBox], registerName)
	names = facenet.judge(features)
	#print(len(boxes), len(names))
	for i in range(len(boxes)):
		cv2.rectangle(frame, (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][2]), int(boxes[i][3])), (0, 0, 255), 2)
		cv2.putText(frame, names[i], ((int(boxes[i][0]), int(boxes[i][1]))), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)
	# 顯示圖片
	cv2.imshow('frame', frame)
	# 若按下 q 鍵則離開迴圈
	if 0xFF == ord('q'):
		break
# 釋放攝影機
cap.release()
# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()