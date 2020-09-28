import cv2
import time
import requests
import json
def boxToImg(img, boxes):
    returnImg = []
    if(type(boxes) == type(None)):
        return []
    for i in range(len(boxes)):
        x1 = int(boxes[i][0] * 3)
        y1 = int(boxes[i][1] * 3)
        x2 = int(boxes[i][2] * 3)
        y2 = int(boxes[i][3] * 3)
        if(x1 < 0):
            x1 = 0
        if(y1 < 0):
            y1 = 0
        if(x2 < 0):
            x2 = 0
        if(y2 < 0):
            y2 = 0
        tempImg = cv2.resize(img[y1:y2, x1:x2], (160, 160), interpolation=cv2.INTER_CUBIC)
        tempImg = cv2.cvtColor(tempImg, cv2.COLOR_BGR2RGB)
        tempImg = tempImg.transpose((2, 0, 1))
        returnImg.append(tempImg.tolist())
    return returnImg
cap = cv2.VideoCapture(0)
registerName = "Joe"
while(1):
    start = time.time()
    ret,frame = cap.read()
    shape = frame.shape
    outframe = cv2.resize(frame, (int(shape[1]/3), int(shape[0]/3)), interpolation=cv2.INTER_CUBIC)
    
    res = {"image": str(outframe.tolist())}
    returnData = requests.post("http://10.25.4.204:8090/detect",json=res)
    boxes = json.loads(returnData.text)
    # for i in range(len(boxes)):
    #     boxes[i][0] = int(boxes[i][0]) - 5
    #     boxes[i][1] = int(boxes[i][1]) - 15
    #     boxes[i][2] = int(boxes[i][2]) + 5
    #     boxes[i][3] = int(boxes[i][3]) + 15
    print(boxes)

    key = cv2.waitKey(1)
    print(key)
    if(key == 43):
        if(registerName == ""):
            registerName = input("Register Name : ")
        if(len(boxes) != 0):
            maxBox = -1
            maxNum = -1
            for i in range(len(boxes)):
                temp = abs(boxes[i][0]-boxes[i][2]) * abs(boxes[i][1]-boxes[i][3])
                if(temp > maxNum):
                    maxNum = temp
                    maxBox = i

            img = boxToImg(frame, [boxes[maxBox]])

            res = {"image": str(img),"name": registerName}
            returnData = requests.post('http://10.25.4.204:8090/register',json=res)
            print(returnData.text)
        else:
            print("No Face In Cemera")
    elif(key == 45):
        registerName = input("Register Name : ")
        print("name change ", registerName)
    else:
        if(len(boxes) != 0):
            imgs = boxToImg(frame, boxes)
            print(len(imgs))
            res = {"images": str(imgs)}
            returnData = requests.post("http://10.25.4.204:8090/judge",json=res)
            names = json.loads(returnData.text)
                 
            for i in range(len(boxes)):
                x1 = int(boxes[i][0] * 3)
                y1 = int(boxes[i][1] * 3)
                x2 = int(boxes[i][2] * 3)
                y2 = int(boxes[i][3] * 3)

                cv2.rectangle(frame,(x1, y1),(x2, y2),(0,0,255),2)
                cv2.putText(frame,names[i],(x1, y1),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
    cv2.imshow("frame", frame)
    print(time.time() - start)