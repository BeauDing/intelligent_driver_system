import time
import RPi.GPIO as GPIO


class KeyPad():
    KEYPAD=[
        ['1','2','3','A'],
        ['4','5','6','B'],
        ['7','8','9','C'],
        ['*','0','#','D']]
 
    ROW    =[12,16,20,21]#行
    COLUMN =[6,13,19,26]#列
 
    #初始化函数
    def __init__(self):
        # GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
    #取得键盘数函数
    def getkey(self):
        GPIO.setmode(GPIO.BCM)
        #设置列输出低
        for i in range(len(self.COLUMN)):
          GPIO.setup(self.COLUMN[i],GPIO.OUT)
          GPIO.output(self.COLUMN[i],GPIO.LOW)
        #设置行为输入、上拉
        for j in range(len(self.ROW)):
          GPIO.setup(self.ROW[j],GPIO.IN,pull_up_down=GPIO.PUD_UP)

        #检测行是否有键按下，有则读取行值
        RowVal=-1
        for i in range(len(self.ROW)):
          RowStatus=GPIO.input(self.ROW[i])
          if RowStatus==GPIO.LOW:
             RowVal=i
             #print('RowVal=%s' % RowVal)
        #若无键按下,则退出，准备下一次扫描
        if RowVal<0 or RowVal>3:
          self.exit()
          return

        #若第RowVal行有键按下，跳过退出函数，对掉输入输出模式
        #第RowVal行输出高电平，
        GPIO.setup(self.ROW[RowVal],GPIO.OUT)
        GPIO.output(self.ROW[RowVal],GPIO.HIGH)
        #列为下拉输入
        for j in range(len(self.COLUMN)):
          GPIO.setup(self.COLUMN[j],GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

        #读取按键所在列值
        ColumnVal=-1
        for i in range(len(self.COLUMN)):
          ColumnStatus=GPIO.input(self.COLUMN[i])
          if ColumnStatus==GPIO.HIGH:
            ColumnVal=i
        #等待按键松开
            while GPIO.input(self.COLUMN[i])==GPIO.HIGH:
              time.sleep(0.05)
              #print ('ColumnVal=%s' % ColumnVal)
        #若无键按下，返回
        if ColumnVal<0 or ColumnVal>3:
          self.exit()
          return

        self.exit()
        return self.KEYPAD[RowVal][ColumnVal]

    #退出函数
    def exit(self):

        # import RPi.GPIO as GPIO
        for i in range(len(self.ROW)):
          GPIO.setup( self.ROW[i],GPIO.IN,pull_up_down=GPIO.PUD_UP)
        for j in range(len( self.COLUMN)):
          GPIO.setup( self.COLUMN[j],GPIO.IN,pull_up_down=GPIO.PUD_UP)
 
    #获取输入字符串 
    def getStr(self):
        print('program into getStr')
        a = ''
        key = None
        while True:
            
            key = self.getkey()
            if not key == None:
                print('you input ',key)
                if key=='*':
                    print('begin to collect string')
                    a = ''
                elif key=='#':
                    print('collect over')
                    return a
                else:
                    a = a + key
                

if __name__ == '__main__':
    print('please press * to begin and press # to end')
    keypad=KeyPad()
    myStr = keypad.getStr()
    print('your string is',myStr)
        
