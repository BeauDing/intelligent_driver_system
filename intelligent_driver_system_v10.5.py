# _*_ coding:utf-8 _*_
from LCD import Adafruit_CharLCD
from pygame import mixer
import face_recognition
import cv2
# import numpy as np
from scipy.spatial import distance as dis
from imutils import face_utils
import imutils
import dlib
import time
import pickle
from gpiozero import Buzzer
from gpiozero import Button
import time
import datetime
from KeyBoard import KeyPad
from AddIdentity_key import AddIdentity

'''
智能驾驶检测系统

（1）face_recognition.compare_faces内部属性
     tolerance 容错率：在添入beau_ding后修改为0.39，
                       在填入zihao_qi后修改为0.55，
（2）button_flag用于检测按键的状态，设置两个按键，
     一个用于开始程序，一个用于复位（跳出人脸识别和疲惫检测的循环）
（3）采用gpiozero库导入Button和Buzzer，可以有效的控制蜂鸣器和检测按键

'''

class IntelligentDriverSystem():

    button_start = Button(2)
    button_reset = Button(3)
    buzzer = Buzzer(4)
    button_flag = 0
    collectError =0

    # args={'encodings':'encodings_test_v5.pickle','detection_method':'hog'}
    args={'encodings':'data/encoding_test.pickle','detection_method':'hog'}


    def __init__(self):
        from pygame import mixer
        mixer.init()
        mixer.music.load('begin.mp3')
        mixer.music.play()
        addIdentity=AddIdentity()
        lcd = Adafruit_CharLCD()
        lcd.clear()  
        Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        lcd.message("Welcome! time is\n"+Time)

        self.buzzer.blink(0.1)
        time.sleep(3)    
        self.buzzer.off()

        # print("Enter the password")
        # button_begin_result = self.start_up()

        while True:
            print("Enter the password")
            button_begin_result = self.start_up()
            if button_begin_result==2:
                print("Enter the main program.")
                self.collectError = 0
                break
            elif button_begin_result==1:
                print("Enter the add program.")
                self.collectError = 0
                addIdentity.Add(lcd)
                break
            else:
                self.collectError += 1
                print("Error {:d} times.Please enter the password again.".format(self.collectError))
                errormessage="Error {:d} times.\nPlease try again.".format(self.collectError)

                lcd.clear()
                lcd.message(errormessage)

                if self.collectError >= 3:
                    self.buzzer.blink(0.1)
                    time.sleep((self.collectError-2)*5.0)
                    self.buzzer.off()


        while True:
            print("print the white button to start the program.")
            if self.button_start.is_pressed:
            # button_begin_result = self.button_start()
            # print('button_begin_result',button_begin_result)
            # print('button_begin_result.type',type(button_begin_result))
            # if (button_begin_result==1) or (button_begin_result == 2):
                mixer.music.stop()
                self.buzzer.blink(0.5)
                time.sleep(1)
                self.buzzer.off()
                

                print("***************BEGIN****************")
                print("[INFO] STEP ONE - face recognition")

                lcd.clear()
                lcd.message("face recognition")

                # driverface_recognition(args={'encodings':'encodings_test_v3.pickle','output':'output/webcam_face_recognition_output.avi','display':1,'detection_method':'hog'})
                # driverface_recognition(args={'encodings':'encodings_test_v4.pickle','output': None,'display':1,'detection_method':'hog'})
                self.driverface_recognition(Adafruit_CharLCD = lcd)
                
                if self.button_flag:
                    
                    continue

                print("[INFO] waiting...  ")
                lcd.message("waiting...")

                time.sleep(1.0)  #延迟

                lcd.clear()
                lcd.message("fatigue detection")

                print("[INFO] STEP TWO - fatigue detection")

                self.fatigue_detection(Adafruit_CharLCD = lcd)

                lcd.clear()

                print("***************END****************")

            #elif self.button_start() == 1:
            # elif button_begin_result== 1:
             
            #     print("enter addidentity")
            #     #addIdentity=AddIdentity()
            #     addIdentity.Add()
            else:
                
                print("[INFO] waiting...  ")
                lcd.clear()
                lcd.message("waiting...")
                time.sleep(1)
                if self.buzzer.is_active:
                   self.buzzer.off()

    def start_up(self):
        print('=========================')
        print('into button start')
        keypad1=KeyPad()
        namestrs1=keypad1.getStr()
        print("panding")
        if namestrs1=='88888888':
            print("enter 88888888")
            return 2
        elif namestrs1=='666':
            print("enter 666")
            return 1
        else:
            print("failed")
            return 0

    # def button_addIdentity(self):
    #     keypad2=KeyPad()
    #     namestrs2=keypad2.getStr()
    #     if namestrs2=='666':
    #         return True
    #     else:
    #         return False

    # def button_reset(self):
    #     keypad2=KeyPad()
    #     namestrs2=keypad2.getStr()
    #     if namestrs2=='D':
    #         return True
    #     else:
    #         return False

    # #计算嘴的长宽比,euclidean(u, v, w=None)用于计算两点的欧几里得距离
    # def mouthRatio(self,mouth):
    #     left=dis.euclidean(mouth[2],mouth[10])
    #     mid=dis.euclidean(mouth[3],mouth[9])
    #     right=dis.euclidean(mouth[4],mouth[8])
    #     horizontal=dis.euclidean(mouth[0],mouth[6])

    #     return 10.0*horizontal/(3.0*left+4.0*mid+3.0*right)

    #计算眼睛的长宽比
    def eyesRatio(self,eye):
        left = dis.euclidean(eye[1], eye[5])
        right = dis.euclidean(eye[2], eye[4])
        horizontal = dis.euclidean(eye[0], eye[3])
        
        return 2.0*horizontal/(left+right)

    #人脸识别
    def driverface_recognition(self,Adafruit_CharLCD):   
        #引入全局变量，检测按键状态
        # global button_flag
        #人脸识别过程中，驾驶者出现在摄像头前的（时间？）
        Judge = 0     
        #人脸识别过程中，设置的驾驶者出现在摄像头前的（时间？）的阈值
        #若时间达到阈值，则弹出循环进行下一步操作，否则继续执行循环
        flag  = 3     


        # load the known faces and embeddings
        print("[INFO] loading encodings...")
        data = pickle.loads(open(self.args["encodings"], "rb").read())
        #print(data)

        # initialize the video stream and pointer to output video file, then
        # allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        cap = cv2.VideoCapture(0)

        #调节摄像头帧率，目前来看帧率越低越好控制
        cap.set(cv2.CAP_PROP_FPS,2)

        print("[INFO] initializing...")
        # writer = None
        time.sleep(2.0)

        # loop over frames from the video file stream
        while True:
            # grab the frame from the threaded video stream
            if self.button_reset.is_pressed:
            # if self.button_reset():

                Adafruit_CharLCD.clear()
                Adafruit_CharLCD.message("over!")
                time.sleep(1)
                self.button_flag = 1
                mixer.init()
                mixer.music.load('xiaoge.mp3')
                mixer.music.play()
                break
            else:
                self.button_flag = 0

            ret,frame = cap.read()
                
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            rgb = imutils.resize(frame, width=320)
            r = frame.shape[1] / float(rgb.shape[1])
            #print("r: " + str(r))
            
            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb, model= self.args["detection_method"])
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                          encoding , tolerance=0.5)
                name = "Unknown"

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                
                # update the list of names
                names.append(name)

            # loop over the recognized faces
            # for ((top, right, bottom, left), name) in zip(boxes, names):
            #     # rescale the face coordinates
            #     top = int(top * r)
            #     right = int(right * r)
            #     bottom = int(bottom * r)
            #     left = int(left * r)

                # draw the predicted face name on the image
                # cv2.rectangle(frame, (left, top), (right, bottom),
                #     (0, 255, 0), 2)
                # y = top - 15 if top - 15 > 15 else top + 15
                # cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                #     0.75, (0, 255, 0), 2)

            # if the video writer is None *AND* we are supposed to write
            # the output video to disk initialize the writer
            # if writer is None and args["output"] is not None:
            #     fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            #     writer = cv2.VideoWriter(args["output"], fourcc, 20,
            #         (frame.shape[1], frame.shape[0]), True)

            # if the writer is not None, write the frame with recognized
            # faces t odisk
            # if writer is not None:
            #     writer.write(frame)
            
            print("检测到",names)
            if(len(names) > 0):
                namestrs=""
                for namestr in names:
                    namestrs+=namestr+','            
                Adafruit_CharLCD.clear()
                # Adafruit_CharLCD.message(str(names[0])+str(Judge))
                Adafruit_CharLCD.message(namestrs)
                
            else:
                Adafruit_CharLCD.clear()
                Adafruit_CharLCD.message('NO RECOGNITION')
            #lcd.clear()
            #lcd.message(str(names[0]))
            #判定：如果检测到脸且持续存在，则Judge持续计数，否则，Judge自动归零
            if ("Unknown" not in names) & (len(names)>0):
                Judge = Judge+1
            else:
                Judge = 0;

            # check to see if we are supposed to display the output frame to
            # the screen
            # if args["display"] > 0:
            #cv2.imshow("Frame", frame)

            #key = cv2.waitKey(1) & 0xFF
            #if key == ord("Q"):  exit()


            #识别判定，识别熟人弹出循环；识别生人，死循环
            if (Judge > flag) & ("Unknown" not in names) & (len(names)>0):
                self.buzzer.blink(0.1)
                Adafruit_CharLCD.clear()
                Adafruit_CharLCD.message("hello!" + name)
                time.sleep(2)
                self.buzzer.off()
                break
            
            # Judge=Judge+1

            #停止


        # do a bit of cleanup
        #cv2.destroyAllWindows()

        # vs.stop()

        # check to see if the video writer point needs to be released
        # if writer is not None:
        #     writer.release()

    #倦意检测
    def fatigue_detection(self,Adafruit_CharLCD):
        #眼睛长宽比的阈值，如果超过这个值就代表眼睛长/宽大于采集到的平均值，默认已经"闭眼"
        eyesRatioLimit=0
        #数据采集的次数
        collectCountInterval=40
        #数据采集的计数，采集collectCountInterval次然后取平均值
        collectCount=0
        #用于数据采集的求和
        collectSum=0
        #是否开始检测
        startCheck=False
        #统计"闭眼"的次数
        eyesCloseCount=0

        #初始化dlib
        detector=dlib.get_frontal_face_detector()
        predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        #获取面部各器官的索引
        #左右眼
        (left_Start,left_End)=face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (right_Start,right_End)=face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        # #嘴
        # (leftMouth,rightMouth)=face_utils.FACIAL_LANDMARKS_IDXS['mouth']
        # #下巴
        # (leftJaw,rightJaw)=face_utils.FACIAL_LANDMARKS_IDXS['jaw']
        # #鼻子
        # (leftNose,rightNose)=face_utils.FACIAL_LANDMARKS_IDXS['nose']
        # #左右眉毛
        # (left_leftEyebrow,left_rightEyebrow)=face_utils.FACIAL_LANDMARKS_IDXS['left_eyebrow']
        # (right_leftEyebrow,right_rightEyebrow)=face_utils.FACIAL_LANDMARKS_IDXS['right_eyebrow']

        #开启视频线程，延迟
        print("[INFO] starting video stream...")
        cap = cv2.VideoCapture(0)
        #调节摄像头帧率
        cap.set(cv2.CAP_PROP_FPS,2)   
        #调整摄像头分辨率
        # ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,240)
        # ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,130)
        
        #初始化
        print("[INFO] initializing...")
        time.sleep(2.0)
        
        #循环检测
        while True:
            
            
            #对每一帧进行处理，设置宽度并转化为灰度图
            ret,frame = cap.read()
            #print('collect data')
            frame = imutils.resize(frame, width=320)
            #转换为GRAY颜色空间
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            #检测灰度图中的脸
            faces = detector(img, 0)
            for k in faces:
                #确定面部区域的面部特征点，将特征点坐标转换为numpy数组
                shape = predictor(img, k)
                shape = face_utils.shape_to_np(shape)

                #左右眼
                leftEye = shape[left_Start:left_End]
                rightEye = shape[right_Start:right_End]
                leftEyesVal = self.eyesRatio(leftEye)
                rightEyesVal = self.eyesRatio(rightEye)
                #凸壳
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                #绘制轮廓
                cv2.drawContours(img, [leftEyeHull], -1, (0, 0, 0), 1)
                cv2.drawContours(img, [rightEyeHull], -1, (0, 0, 0), 1)
                #取两只眼长宽比的的平均值作为每一帧的计算结果
                eyeRatioVal = (leftEyesVal + rightEyesVal) / 2.0

                # #嘴
                # mouth=shape[leftMouth:rightMouth]
                # mouthHull=cv2.convexHull(mouth)
                # cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

                # #鼻子
                # nose=shape[leftNose:rightNose]
                # noseHull=cv2.convexHull(nose)
                # cv2.drawContours(frame, [noseHull], -1, (0, 255, 0), 1)

                # #下巴
                # jaw=shape[leftJaw:rightJaw]
                # jawHull=cv2.convexHull(jaw)
                # cv2.drawContours(frame, [jawHull], -1, (0, 255, 0), 1)

                # #左眉毛
                # leftEyebrow=shape[left_leftEyebrow:left_rightEyebrow]
                # leftEyebrowHull=cv2.convexHull(leftEyebrow)
                # cv2.drawContours(frame, [leftEyebrowHull], -1, (0, 255, 0), 1)

                # #右眉毛
                # rightEyebrow=shape[right_leftEyebrow:right_rightEyebrow]
                # rightEyebrowHull=cv2.convexHull(rightEyebrow)
                # cv2.drawContours(frame, [rightEyebrowHull], -1, (0, 255, 0), 1)

                if collectCount < collectCountInterval:
                    collectCount+=1
                    collectSum+=eyeRatioVal
                    # cv2.putText(img, "DATA COLLECTING", (10, 10),cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
                    print("[INFO] DATA COLLECTING...  ")

                    Adafruit_CharLCD.clear()
                    Adafruit_CharLCD.message("DATA COLLECTING")

                    startCheck=False
                else:
                    if not startCheck:
                        eyesRatioLimit=collectSum/(1.0*collectCountInterval)
                        # Adafruit_CharLCD.clear()
                        Adafruit_CharLCD.clear()
                        Adafruit_CharLCD.message("fatigue detection")

                        print('眼睛长宽比均值',eyesRatioLimit)
                        # eyesRatioLimit = round(eyesRatioLimit,2)
                        # AverageEyesRatio = str(eyesRatioLimit)
                    startCheck=True

                # Adafruit_CharLCD.clear()
                # Adafruit_CharLCD.message("fatigue detection")

                if startCheck:
                    #如果眼睛长宽比大于之前检测到的阈值，则计数，闭眼次数超过50次则认为已经"睡着"
                    if eyeRatioVal > 1.11*eyesRatioLimit:
                        eyesCloseCount += 1
                        if eyesCloseCount >= 22:
                            # cv2.putText(frame, "SLEEP!!!", (580, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            # cv2.putText(img, "SLEEP!!!",   (60, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
                            # if eyesCloseCount%2 == 0 :

                            #Adafruit_CharLCD.clear()
                            #Adafruit_CharLCD.message(str(eyesCloseCount)+'/n sleep!')
                            #time.sleep(0.1)
                            #Adafruit_CharLCD.message("sleep!")
                            self.buzzer.blink(0.3)
                            #time.sleep(0.5)
                        elif eyesCloseCount >= 4:
                            # cv2.putText(img, "EXHAUSTED!", (60, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
                            # if eyesCloseCount%2 == 0 :                        
                            
                            #Adafruit_CharLCD.clear()
                            #Adafruit_CharLCD.message('close'+str(eyesCloseCount)+'/n exhausted!')
                            #time.sleep(0.1)
                          #  Adafruit_CharLCD.message('close'+"exhausted!")
                            self.buzzer.blink(0.1)
                            
                            #time.sleep(0.5)
                        elif eyesCloseCount >= 0:
                            # cv2.putText(img, "WIDE AWAKE", (60, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
                            #
                            #Adafruit_CharLCD.clear()
                            #Adafruit_CharLCD.message('close'+str(eyesCloseCount)+'/n Wake!')
                            #time.sleep(0.1)
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            #time.sleep(0.5)
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))                            
                            
                            # Adafruit_CharLCD.message("Wake!")
                            #print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            #print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            self.buzzer.off()
                        # alarm_beep(eyesCloseCount)

                    else:  
                        eyesCloseCount = 0

                    print('眼睛实时长宽比:{:.2f} '.format(eyeRatioVal/eyesRatioLimit))
                    # eyeRatioVal = round(eyeRatioVal,2)
                    # Adafruit_CharLCD.clear()
                    #Adafruit_CharLCD.message('av:'+AverageEyesRatio+'\n now:'+str(eyeRatioVal))
                    
                    #眼睛长宽比
                    # cv2.putText(img, "EYES_RATIO: {:.2f}".format(eyeRatioVal), (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
                    #闭眼次数
                    # cv2.putText(img,"EYES_COLSE: {}".format(eyesCloseCount),(40,30),cv2.FONT_HERSHEY_SIMPLEX,0.2,(0,0,0),1)

                    #通过检测嘴的长宽比检测有没有打哈欠，后来觉得没什么用
                    # cv2.putText(frame,"MOUTH_RATIO: {:.2f}".format(mouthRatio(mouth)),(500, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            #cv2.imshow("Frame", img)

            #key = cv2.waitKey(1) & 0xFF
            #停止
            #if key == ord("S"):  break

            if self.button_reset.is_pressed :
            # if self.button_reset() :
                
                print('program is over')
                mixer.init()
                mixer.music.load('xiaoge.mp3')
                mixer.music.play()
                break
            

        cap.release()
        #cv2.destroyAllWindows()

    # #蜂鸣器控制函数，根据计数返回不同的频率信号，控制蜂鸣器发声
    # def alarm_beep(count):
    #     if count >= 50:
    #         winsound.Beep(2000,200)
    #     elif count >=30:
    #         winsound.Beep(1000,200)
    #     # else:
    #     #     winsound.Beep(500,200);


    #运行流程
            

if __name__ == '__main__':
    intelligent_driver_system=IntelligentDriverSystem()

