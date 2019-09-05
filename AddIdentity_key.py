from imutils import paths
import os
import face_recognition
import cv2
import pickle
import sys
import time
from KeyBoard import KeyPad
from LCD import Adafruit_CharLCD

'''
代码分析：
from imutils import paths 
导入的函数paths.list_images()方法不能正常使用，目前原因未明

'''
class AddIdentity():


    def __init__(self):
        #print("Please press '*' to begin and press '#' to end.")
        # lcd = Adafruit_CharLCD()

        # lcd.clear()
        # lcd.message("Enter the addIdentity program.")
        
        time.sleep(1.0)

        print("initializing...")

        # keypad=KeyPad()
        # namestrs=keypad.getStr()
        # print("your string is " , namestrs)
        # # namestrs=input("Enter your name: ")
        # mkpath="data/" + namestrs
        # self.mkdir(mkpath)
        # # face_capture('G:\MyDownLoads\Anaconda3\items\Test\data')
        # self.face_capture(mkpath)
        # self.AddPickle(namestrs)


    def mkdir(self,path):
        # 引入模块
     
        # 去除首位空格
        path=path.strip()
        # 去除尾部 \ 符号
        path=path.rstrip("/")
     
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists=os.path.exists(path)
     
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path) 
     
            print(path+' 创建成功')
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print(path+' 目录已存在')
            return False



    def face_capture(self,path_name,Adafruit_CharLCD, window_name="GET_FACE", camera_idx=0, catch_pic_num=30):
        # cv2.namedWindow(window_name)

        print("[INFO] starting video stream...")
        # 视频来源，可以来自一段已存好的视频，也可以直接来自USB摄像头
        cap = cv2.VideoCapture(camera_idx)

        cap.set(cv2.CAP_PROP_FPS,2)
        # 告诉OpenCV使用人脸识别分类器
        classfier = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt.xml")

        # 识别出人脸后要画的边框的颜色，RGB格式
        color = (0, 255, 0)
        num = 0

        print("[INFO] initializing...")
        time.sleep(1.0)

        while cap.isOpened():
            ok, frame = cap.read()  # 读取一帧数据
            #print(type(frame))
            if not ok:
                break

            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将当前桢图像转换成灰度图像

            # 人脸检测，1.2和2分别为图片缩放比例和需要检测的有效点数
            faceRects = classfier.detectMultiScale(grey, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
            if len(faceRects) > 0:  # 大于0则检测到人脸
                for faceRect in faceRects:  # 单独框出每一张人脸
                    x, y, w, h = faceRect

                    # 将当前帧保存为图片
                    img_name = '%s/%d.jpg ' % (path_name, num)
                    image = frame[y - 10: y + h + 10, x - 10: x + w + 10]
                    cv2.imwrite(img_name, image)

                    num += 1
                    if num > (catch_pic_num):  # 如果超过指定最大保存数量退出循环
                        break

                    # 画出矩形框
                    # cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), color, 2)

                    # 显示当前捕捉到了多少人脸图片了，这样站在那里被拍摄时心里有个数，不用两眼一抹黑傻等着
                    # font = cv2.FONT_HERSHEY_SIMPLEX
                    # cv2.putText(frame, 'num:%d' % (num), (x + 30, y + 30), font, 1, (255, 0, 255), 4)

                    Adafruit_CharLCD.clear()
                    # Adafruit_CharLCD.message("processing \nimage {}/{}".format(i + 1,len(imagePaths)))
                    Adafruit_CharLCD.message("capturing \nimage {}/{}".format(num,catch_pic_num))
                    time.sleep(0.1)

                    # 超过指定最大保存数量结束程序
            if num > (catch_pic_num): break

            # 显示图像
            # cv2.imshow(window_name, frame)
            # c = cv2.waitKey(10)
            # if c & 0xFF == ord('q'):
            #     break

                # 释放摄像头并销毁所有窗口
        cap.release()
        # cv2.destroyAllWindows()

    def AddPickle(self,namestrs,Adafruit_CharLCD):

        path="data/encoding_test.pickle"
        isExists=os.path.exists(path)

        # print("namestrs:",namestrs)

        #如果pickle文件不存在，则新建一个空pickle文件
        if not isExists:
            print(path + '创建pickle文件成功')
            olddata={}
            olddata["encodings"]=[]
            olddata["names"]=[]
            f = open("data/encoding_test.pickle","wb")
            f.write(pickle.dumps(olddata))
            f.close()
        else:
            print(path + '文件已存在')
        #如果pickle文件存在，则直接进行下一步操作
        # print("namestrs:",namestrs)


        # imagePaths = list(paths.list_images("data/" + namestrs))
        listimages=os.listdir('data/'+namestrs+'/')
        imagePaths=[]
        for listimage in listimages:
            imagepath='data/'+namestrs+'/'+listimage
            imagePaths.append(imagepath)

        # olddata= pickle.loads(open("G:\\MyDownLoads\\Anaconda3\\items\\Test\\data\\encoding_test.pickle", "rb").read())
        olddata= pickle.loads(open("data/encoding_test.pickle", "rb").read())
        
        # print(imagePaths)
        # print(len(imagePaths))
        # print(enumerate(imagePaths))

        knownEncodings = []
        knownNames = []


        for (i, imagePath) in enumerate(imagePaths):
        #     print(imagePath)
        # print("now imagePath : ",imagePath)
        # print(imagePath.split(os.path.sep)[-2])
            print("[INFO] processing image {}/{}".format(i + 1,len(imagePaths)))
            print("Loading...")

            Adafruit_CharLCD.clear()
            Adafruit_CharLCD.message("processing \nimage {}/{}".format(i + 1,len(imagePaths)))
            time.sleep(0.1)

            image=cv2.imread(imagePath)
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

            boxes=face_recognition.face_locations(rgb,model='hog')

            encodings=face_recognition.face_encodings(rgb,boxes)

            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(namestrs)

        data = {"encodings": knownEncodings, "names": knownNames}
        olddata["encodings"].extend(data["encodings"])
        olddata["names"].extend(data["names"])

        f = open("data/encoding_test.pickle", "wb")
        f.write(pickle.dumps(olddata))
        f.close()

    def Add(self,Adafruit_CharLCD):
        print("Please press '*' to begin and press '#' to end.")
        
        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("Enter the addIdentity program.")
        time.sleep(1.0)

        #输入建立的图片文件夹的名称
        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("Input your id.")
        time.sleep(1.0)
        keypad=KeyPad()
        namestrs=keypad.getStr()
        print("your string is " , namestrs)

        #建立该文件夹
        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("Your id is\n" + namestrs)
        time.sleep(3.0)
        # namestrs=input("Enter your name: ")
        mkpath="data/" + namestrs
        self.mkdir(mkpath)
        # face_capture('G:\MyDownLoads\Anaconda3\items\Test\data')
        
        #开始捕捉图片
        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("Capture.")
        time.sleep(3.0)
        self.face_capture(path_name=mkpath,Adafruit_CharLCD=Adafruit_CharLCD)
        
        #开始编码
        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("encoding...")
        time.sleep(3.0)
        self.AddPickle(namestrs=namestrs,Adafruit_CharLCD=Adafruit_CharLCD)

        Adafruit_CharLCD.clear()
        Adafruit_CharLCD.message("Finish.")
        time.sleep(3.0)        
       
if __name__ == '__main__':
    addIdentity = AddIdentity()
    addIdentity.Add()