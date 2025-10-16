from datetime import datetime
import os, errno
import time
import io, re
import sqlite3
#import pandas as pd
import subprocess
import atexit
import matrixux
import qr_validator
from PyQt5.QtCore import QThread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QTimer,QDateTime
import socket
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import settings
import getpass
import socket
import fcntl
import struct
import signal
import serial
import threading
import select
import binascii
import mmap
mutex_wrkrbusy = threading.Lock()

cube="NA"
line="NA"
user="NA"
trigger=False
inscanner=True
global text
text='--'
synch_serialthread=1

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(0)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception as e:
        return "No network"

def loadsettings():
    with open('/SCANNER/location.json', "r") as jason_in:
        data = json.load(jason_in) 
        global line,cube,trigger,inscanner
        cube=data['cube']
        line=data['line']
        if data['trigger']=='1':
            trigger=True
        else:
            trigger=False
        if data['scanner']=='1':
            inscanner=True
        else:
            inscanner=False 
                    
class Window2(QMainWindow):   
    global line,cube,user,trigger
    def __init__(self):
        super(Window2, self).__init__()
        self.w = settings.Ui_SETTINGSw()
        self.w.setupUi(self)
        
        self.cubet=cube
        self.linet=line
        self.triggert=trigger
        self.inscannert=inscanner
        
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setCapitalization(QFont.AllUppercase)
        self.w.spinBoxline.setFont(font)
        
        #font = w.spinBoxcube.font()
        #font.setCapitalization(QFont.AllUppercase)
        self.w.spinBoxcube.setFont(font)
        
        self.w.curline.setText("Current line: "+line)

        self.w.curcube.setText("Current cubicle: "+cube)
        
        self.w.spinBoxline.setProperty("value", int(line, 32))
        self.w.spinBoxcube.setProperty("value", cube)
        
        self.w.checkBox.setChecked(self.triggert)
        self.w.checkBox_2.setChecked(self.inscannert)


        self.w.save.clicked.connect(self.save_clicked)
        self.w.exit.clicked.connect(self.exit_clicked)
        self.w.pushButton.clicked.connect(self.bluetooth_clicked)
        #resetcount
        self.w.pushButton_2.clicked.connect(self.reset_clicked)
        
        
        self.w.label_2 = QLabel('Version:1.0', self)
        pal = self.w.label_2.palette()
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("red"))
        self.w.label_2.setPalette(pal)
        self.w.label_2.move(330, 1)
        #self.w.label_2.setGeometry(QtCore.QRect(330, 5, 141, 20))
        #self.w.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 90);") 
        self.w.label_2.setHidden(False)

    @QtCore.pyqtSlot()   
    def save_clicked(self):
        global trigger
        convTable = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V')
        self.linet=str(convTable[self.w.spinBoxline.value()])
        self.cubet=str(self.w.spinBoxcube.value())
        with open('/SCANNER/location.json', "r+") as outfile: 
            data = json.load(outfile)
            data["line"] =self.linet
            data["cube"] =self.cubet
            if self.w.checkBox.isChecked() == True:
                data["trigger"]='1'
            else:
                data["trigger"]='0'
            if self.w.checkBox_2.isChecked() == True:
                data["scanner"]='1'
            else:
                data["scanner"]='0'
            outfile.seek(0)  # rewind
            json.dump(data, outfile)
            outfile.truncate()

        loadsettings()
        
        self.w.curline.setText("Current line : "+line)
        self.w.curcube.setText("Current cubicle : "+cube)
        self.w.checkBox.setChecked(trigger)
        self.w.checkBox_2.setChecked(inscanner)
        
        
    @QtCore.pyqtSlot()    
    def reset_clicked(self): 
        
        self.matrix_db = sqlite3.connect('/SCANNER/scanner.db')    
        
        with open("/SCANNER/cat", "w") as fc:
            cursor6 = self.matrix_db.cursor()#
            cursor6.execute('''SELECT SEQ from sqlite_sequence WHERE name='cartridge';''')
            fc.write(str(cursor6.fetchone()[0])) 
            cursor6.close()    
    
        #print("reset")
    
    @QtCore.pyqtSlot()  
    def exit_clicked(self):
        print("exit") 
        sys.exit()
        
    @QtCore.pyqtSlot()  
    def bluetooth_clicked(self):
        with open("/tmp/python_c_sync/dmy", "w") as f:
            f.seek(0)
            f.write("nothing")

def close_gpio(fd,pin):
        try:
            os.close(fd)
        except OSError as e:
            raise OSError(e.errno, "Closing GPIO: " + e.strerror)
        gpio_path = "/sys/class/gpio/gpio%d" % pin
        if not os.path.isdir(gpio_path):
            try:
                with open("/sys/class/gpio/unexport", "w") as f_export:
                    f_export.write("%d\n" % pin)
            except IOError as e:
                print("Export:"+str(e))     
     
def set_gpio(fd,value):
    try:
        if value:
            os.write(fd, b"1\n")
        else:
            os.write(fd, b"0\n")
    except OSError as e:
        raise OSError(e.errno, "Writing GPIO: " + e.strerror)
    try:
        os.lseek(fd, 0, os.SEEK_SET)
    except OSError as e:
        raise OSError(e.errno, "Rewinding GPIO: " + e.strerror)
          
def poll_gpio(fd):
    p = select.epoll()
    p.register(fd, select.EPOLLIN | select.EPOLLET | select.EPOLLPRI)
    # Poll twice, as first call returns with current state
    for _ in range(2):
        events = p.poll(None)
    # If GPIO edge interrupt occurred
    if events:
        # Rewind
        try:
            os.lseek(fd, 0, os.SEEK_SET)
        except OSError as e:
            raise OSError(e.errno, "Rewinding GPIO: " + e.strerror)    
        
def init_gpio(pin,direction,edge="rising"):
    #"in", "out", "high", "low" #https://www.raspberrypi.org/forums/viewtopic.php?t=5185
    retry=5
    while True:
        try:
            gpio_path = "/sys/class/gpio/gpio%d" % pin
            if not os.path.isdir(gpio_path):
                try:
                    with open("/sys/class/gpio/export", "w") as f_export:
                        f_export.write("%d\n" % pin)
                except Exception as e:
                    print("Export:"+str(e))
            time.sleep(0.1)
            try:
                with open("/sys/class/gpio/gpio%d/direction" % pin, "w") as f_direction:
                    f_direction.write(direction + "\n")
            
            except IOError as e:
                print("direction:"+str(e))
            
            try:
                fd = os.open("/sys/class/gpio/gpio%d/value" % pin, os.O_RDWR)
            except OSError as e:
                print("open:"+str(e))
            if direction=='in':
                try:
                    with open("/sys/class/gpio/gpio%d/edge" % pin, "w") as f_edge: 
                        f_edge.write(edge + "\n")
                except IOError as e:
                    print("f_edge:"+str(e))
            return fd
        except Exception as e:
            print(e)
            retry-=1
            if retry>0:
                continue
            else:
                print("Gpio import error after 5 retries")
                return None           

class matrix_gui(QtWidgets.QDockWidget):
    def __init__(self):
        try:
            super(matrix_gui, self).__init__()
            self.ui = matrixux.Ui_DockWidget()
            #self.ui.setWindowFlag(Qt.FramelessWindowHint) 
            self.ui.setupUi(self)
            self.setGeometry(0, 0, 480, 325) 

            self.ui.qr_input = QtWidgets.QLineEdit(self.ui.dockWidgetContents)
            self.ui.qr_input.setGeometry(QtCore.QRect(440, 10, 300, 28))
            self.ui.qr_input.setReadOnly(False)
            self.ui.qr_input.setFocus()
            self.ui.qr_input.returnPressed.connect(self.qrinput)
            self.ui.qr_input.setFocusPolicy(Qt.StrongFocus)
            qr_inputfont= QtGui.QFont()
            qr_inputfont.setPointSize(18)
            qr_inputfont.setBold(False)
            #qr_inputfont.setWeight(40)
            self.ui.qr_input.setFont(qr_inputfont)
            
            
            global line,cube,user,trigger,inscanner
            loadsettings()

            try :
                self.uart = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=None,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS
                            )
            except Exception as e:
                print("UART. init:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                print(e)
                self.signals.error_signal.emit('UART not found! - '+str(e),'UART init. error')
                time.sleep(255)
                sys.exit()
                
            self.mutex = QMutex()
            self.cond = QWaitCondition()    

            self.threadpool = QThreadPool()
            
            self.worker = Worker(self.mutex,self.cond,self.uart)
            self.timerthread =TimerThread(self.ui)
            if inscanner==True:
                self.serialcom=SerialThread(self.cond, self.uart)
            #self.shutdownmonitor=ShutdownThread()
            

            
            self.ui.MATRIX_EDIT.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)    
            self.ui.CARTRIDGE_EDIT.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.worker.signals.change_value_matrix.connect(self.set_MATRIX_EDIT)
            self.worker.signals.change_value_cartridge.connect(self.set_CARTRIDGE_EDIT)
            #self.worker.signals.change_value_count.connect(self.set_CARTRIDGE_COUNT)
            
            self.worker.signals.change_acceptvalue_count.connect(self.set_CARTRIDGE_COUNT_1)
            self.worker.signals.change_rejectvalue_count.connect(self.set_CARTRIDGE_COUNT_2)
            
            
            self.worker.signals.change_value_errors.connect(self.set_ERRORS)
            self.worker.signals.error_signal.connect(self.showdialog)
            self.ui.pushButton_4.setEnabled(False)
            
            if inscanner==True:
                self.serialcom.signals.error_signal.connect(self.showdialog)  
                
            #self.shutdownmonitor.signals.ShutdownSignal.connect(self.shutdown_poc)
            if trigger==True:   
                self.ui.label_2 = QLabel(' WAITING FOR TRIGGER...', self)
                #self.ui.label_2.move(140, 100)
                #self.ui.label_2.setGeometry(QtCore.QRect(23, 210, 225, 25))
                self.ui.label_2.setGeometry(QtCore.QRect(33, 310, 225, 25))
                self.ui.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 90);") 
                self.ui.label_2.setHidden(True)
                if inscanner==True:
                    self.serialcom.signals.waitfortrigon.connect(self.trigwaiton)
                    self.serialcom.signals.waitfortrigoff.connect(self.trigwaitoff)
                    self.ui.pushButton_4.setEnabled(True)
                    self.ui.pushButton_4.clicked.connect(self.trig_scan)
                    
            
                
            self.ui.pushButton_2.clicked.connect(self.logoff)

            self.timerthread.signals.update_time.connect(self.updatetime)
            self.timerthread.signals.update_jigdetails.connect(self.updatejigdetails)
            self.timerthread.signals.update_jigip.connect(self.updatejigip)
            self.timerthread.signals.error_signal.connect(self.showdialog)

            user=getpass.getuser()
            if user=="Operator":
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton_3.setEnabled(False)
            else :
                self.ui.pushButton.clicked.connect(self.window2)
                self.ui.pushButton_3.clicked.connect(self.show_keyboard)
                
            self.ui.WRKSTNin.setFontPointSize(18);
            self.ui.WRKSTNin.setTextColor(QColor(0, 0, 255));
            self.ui.WRKSTNin.setFontWeight(QtGui.QFont.Normal)

            self.ui.MATRIX_EDIT.setFontPointSize(18);#fs
            self.ui.MATRIX_EDIT.setTextColor(QColor(255, 0, 0));
            self.ui.MATRIX_EDIT.setFontWeight(QtGui.QFont.Bold)
            
            self.ui.CARTRIDGE_EDIT.setFontPointSize(18);#18
            self.ui.CARTRIDGE_EDIT.setTextColor(QColor(255, 0, 0));
            self.ui.CARTRIDGE_EDIT.setFontWeight(QtGui.QFont.Bold)
            
            self.ui.CARTRIDGE_EDIT.setText('SCAN CARTRIDGE')
            
            self.ui.WRKSTNin.setText("Line : "+line+"\t                                                               "+"Cubicle : "+cube+"\t                                        "+"User : "+user+'\n'+'Jig ID : '+self.ui.host+"\t                                                                                                    "+"IP : Fetching")
            
            
            

            self.threadpool.start(self.worker)
            self.threadpool.start(self.timerthread)
            if inscanner==True:
                self.threadpool.start(self.serialcom)
            #self.threadpool.start(self.shutdownmonitor)
            
            
            
            
            
            
        except Exception as e:
                print(e)
    """ 
    def shutdown_poc(self):
        try:
            self.serialcom.stop()
            self.worker.stop()
            #self.hide()
            subprocess.Popen('systemctl poweroff -i',shell=True)
            sys.exit()
        except Exception as e:
            print(e)
    """
    @QtCore.pyqtSlot()
    def trigwaitoff(self):
        self.ui.label_2.setHidden(True) 
    @QtCore.pyqtSlot()
    def trigwaiton(self):
        self.ui.label_2.setHidden(False) 
        
    @QtCore.pyqtSlot(str,str)              
    def showdialog(self,text,error_type):
        try:
            global user
            if inscanner==True:
                self.serialcom.stop()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(error_type)
            if error_type=='In-built QR Reader error' and user=="Operator":
                msg.setInformativeText(text+"\nGo to Settings for disabling in-built QR Reader")
            else:
                msg.setInformativeText(text)
            msg.setWindowTitle("ERROR")
            msg.setStandardButtons(QMessageBox.Ok)
            #self.hide()
            msg.exec_()
            if inscanner==True:
                self.serialcom.stop()
            self.worker.stop()
            if error_type=='In-built QR Reader error':
                if user=="Operator":
                    self.logoff()
                else:
                    self.window2()
            sys.exit()
            
        except Exception as e:
            print(e)        
    def window2(self):
        if inscanner==True:
            self.serialcom.stop()
        self.worker.stop()
        self.w = Window2()
        self.w.show()
        self.hide()
    def trig_scan(self):
        #set_gpio(21,1)    
        global text     
        ser = serial.Serial('/dev/qrscanner', baudrate=115200, timeout=5,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                        )
        tgr_cmd= [0x7E, 0x00, 0x08, 0x01, 0x00, 0x02, 0x01, 0xAB, 0xCD,0x00]
        "".join(map(chr, tgr_cmd))
        ser.write(tgr_cmd)
        read_buf=ser.read(size=7)
        if (read_buf[0] == 0x02 and  read_buf[1] == 0x00 and read_buf[2] == 0x00 and  read_buf[3] == 0x01 and  read_buf[4] == 0x00 and  read_buf[5] == 0x33 and  read_buf[6] == 0x31)!=0:
            text_in=ser.readline(50)
            #text_in=bytes((x for x in text_in if x >= 0x20 and x < 127))
            text_in=text_in.decode() 
            #print('raw qr:'+str(text_in))
            text_in=text_in.strip()
            if len(text_in)>3:
                if text_in != text: 
                    #time.sleep(5)
                    text=text_in
                    self.cond.wakeAll()
                else :
                    time.sleep(0.1)
        
    def show_keyboard(self):
        subprocess.Popen('onboard -x 55 -y 210 -s 690x230',shell=True)
        self.ui.qr_input.setFocus()
        self.keybrdclose = QtWidgets.QPushButton(self.ui.dockWidgetContents)
        self.keybrdclose.setGeometry(QtCore.QRect(50, 128, 250, 36))
        self.keybrdclose.setText('Close Keyboard')
        self.keybrdclose.clicked.connect(self.hide_keyboard)
        self.keybrdclose.show()
        
    def hide_keyboard(self):
        subprocess.Popen('pkill onboard',shell=True)
        self.keybrdclose.clicked.disconnect(self.hide_keyboard)
        self.keybrdclose.setParent(None)
        self.keybrdclose.deleteLater()
    
    def logoff(self):
        if inscanner==True:
            self.serialcom.stop()
        self.worker.stop()
        cmd = 'pkill -u '+user
        os.system(cmd)
        
    @QtCore.pyqtSlot()  
    def qrinput(self):
        global text
        text_in = self.ui.qr_input.text()
        self.ui.qr_input.clear()
        self.ui.qr_input.setFocus()
        try:
            if text_in != text:          
                self.cond.wakeAll()
                text=text_in
        except Exception as e:
            print(e)
           
    @QtCore.pyqtSlot()  
    def updatetime(self):
        self.ui.TIMEin.setText(datetime.now().strftime("%I:%M %p"))

    @QtCore.pyqtSlot()
    def updatejigdetails(self):
        try:   
            self.ui.DATEin.setText(datetime.now().strftime("%d/%m/%y"))
        except Exception as e:
            print(e)

    @QtCore.pyqtSlot()
    def updatejigip(self):
    
        try:
            #self.ui.IPin.setText()
            ip=get_ip_address('wlan0')
            if len(ip) < 6:
                ip='No network'
            self.ui.WRKSTNin.setText("Line : "+line+"\t             "+"Cubicle : "+cube+"\t             "+"User : "+user+'\n'+'Jig ID : '+self.ui.host+"\t             "+"IP : "+ip)
        except Exception as e:
            print(e)            
            
    @QtCore.pyqtSlot(str)   
    def set_MATRIX_EDIT(self, text):
        #print(self.ui)
        try:
            #print(text+"mat edit\n")
            self.ui.MATRIX_EDIT.setText(text)
            #
        except Exception as e:
            print(e)
    
    @QtCore.pyqtSlot(str)     
    def set_CARTRIDGE_EDIT(self, text):
        try:
            #print(text+"mat edit\n")
            self.ui.CARTRIDGE_EDIT.setText(text)
        except Exception as e:
            print(e)
       
    @QtCore.pyqtSlot(str)    
    #def set_CARTRIDGE_COUNT(self, text):
       # try:
       #     #print(text+"mat edit\n")
        ##    self.ui.CARTRIDGE_COUNT.setText(text)
       # except Exception as e:
         #   print(e)
    
    def set_CARTRIDGE_COUNT_1(self, text):
        try:
            #print(text+"mat edit\n")
            self.ui.CARTRIDGE_COUNT_1.setText(text)
        except Exception as e:
            print(e)
    
    def set_CARTRIDGE_COUNT_2(self, text):
        try:
            #print(text+"mat edit\n")
            self.ui.CARTRIDGE_COUNT_2.setText(text)
        except Exception as e:
            print(e)       
            
    @QtCore.pyqtSlot(str)     
    def set_ERRORS(self, text):
        try:
            print(text+" error\n")
        except Exception as e:
            print(e)

class SerialSignals(QObject):
    error_signal=pyqtSignal(str,str)
    waitfortrigon=pyqtSignal()
    waitfortrigoff=pyqtSignal()

class SerialThread(QRunnable):
    def __init__(self, cond, ser_uart):
        super(SerialThread, self).__init__()
        self.signals = SerialSignals()
        self.cond=cond
        self.running=True
        self.trig=trigger
        self.uart=ser_uart
    def stop(self):
        self.running=False
        try:
            self.running=False
            if self.trig==True:
                set_gpio(self.status_pin,0)
                close_gpio(self.trigger_pin,20)
                close_gpio(self.status_pin,21)
            self.ser.close()
            if mutex_wrkrbusy.locked():
                mutex_wrkrbusy.release()
        except Exception as e:
                print(e)
    def run(self):
        global text, mutex_wrkrbusy,synch_serialthread
        try :
            self.ser = serial.Serial('/dev/qrscanner', baudrate=115200, timeout=5,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                        )
        except Exception as e:
            print("Ser. init:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
            print(e)
            self.signals.error_signal.emit('Inbuilt QR Reader not found! - '+str(e),'In-built QR Reader error')
            time.sleep(255)
            sys.exit()
        
        qr_tgr_cmd= [0x7E, 0x00, 0x08, 0x01, 0x00, 0x02, 0x01, 0xAB, 0xCD,0x00]
        "".join(map(chr, qr_tgr_cmd))
        self.sbc_busy_pin=init_gpio(18,'high')
        set_gpio(self.sbc_busy_pin,1)
        if self.trig==True:
            self.trigger_pin=init_gpio(20,'in','rising')
            if (self.trigger_pin==None):
                self.signals.error_signal.emit('Init function returned None','GPIO Init error')
            self.status_pin=init_gpio(21,'high')
            if (self.status_pin==None):
                self.signals.error_signal.emit('Init function returned None','GPIO Init error')
        while synch_serialthread == 1:
            time.sleep(0.1)
        while self.running:
            mutex_wrkrbusy.acquire(blocking=True) 
            try:   
                if self.trig==True:
                    self.signals.waitfortrigon.emit()
                    set_gpio(self.status_pin,1)
                    set_gpio(self.sbc_busy_pin,1)
                    #poll_gpio(self.trigger_pin)
                    uart_buf=[0,0]
                    while True:
                        uart_buf=self.uart.read(size=1)
                        print (uart_buf)
                        if uart_buf[0] is 20:
                            break
                    
                    self.signals.waitfortrigoff.emit()
                    set_gpio(self.status_pin,0)
                    set_gpio(self.sbc_busy_pin,0)
                self.ser.flush()
                #time.sleep(3)
                try:
                    print("Triggering")
                    self.ser.write(qr_tgr_cmd)
                    read_buf=self.ser.read(size=7)
                    print("CMD ERR: "+ str(read_buf[0])+'|'+ str(read_buf[1])+'|'+  str(read_buf[2])+'|'+  str(read_buf[3])+'|'+ str(read_buf[4])+'|'+  str(read_buf[5])+'|'+ str( read_buf[6]))
                except Exception as e:
                    print("Serial QR command exception:")
                    print(e)
                    tgr_cmd= [81]  #Q
                    "".join(map(chr, tgr_cmd))
                    self.uart.write(tgr_cmd)
                    try :
                        self.ser = serial.Serial('/dev/qrscanner', baudrate=115200, timeout=5,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS
                                    )
                    except Exception as e:
                        print("Ser. init:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                        print(e)
                        self.signals.error_signal.emit('Inbuilt QR Reader not found! - '+str(e),'In-built QR Reader error')
                        time.sleep(255)
                        sys.exit()
                    continue
                try: 
                    if (read_buf[0] == 0x02 and  read_buf[1] == 0x00 and read_buf[2] == 0x00 and  read_buf[3] == 0x01 and  read_buf[4] == 0x00 and  read_buf[5] == 0x33 and  read_buf[6] == 0x31)!=0:
                        try:
                            text_in=self.ser.readline(50)
                        except Exception as e:
                            print("Serial QR read exception:")
                            print(e)
                            tgr_cmd= [81]  #Q
                            "".join(map(chr, tgr_cmd))
                            self.uart.write(tgr_cmd)
                            try :
                                self.ser = serial.Serial('/dev/qrscanner', baudrate=115200, timeout=5,
                                            parity=serial.PARITY_NONE,
                                            stopbits=serial.STOPBITS_ONE,
                                            bytesize=serial.EIGHTBITS
                                            )
                            except Exception as e:
                                print("Ser. init:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                                print(e)
                                self.signals.error_signal.emit('Inbuilt QR Reader not found! - '+str(e),'In-built QR Reader error')
                                time.sleep(255)
                                sys.exit()
                            continue
                        #text_in=bytes((x for x in text_in if x >= 0x20 and x < 127))
                        text_in=text_in.decode() 
                        #print('raw qr:'+str(text_in))
                        text_in=text_in.strip()
                        if len(text_in)>3:
                            if text_in != text: 
                                #time.sleep(5)
                                text=text_in
                                if mutex_wrkrbusy.locked():
                                    mutex_wrkrbusy.release()
                                self.cond.wakeAll()
                                continue
                            else :
                                print("Cont. error")
                                tgr_cmd= [67]  #C
                                "".join(map(chr, tgr_cmd))
                                self.uart.write(tgr_cmd)
                                time.sleep(0.5)
                                if mutex_wrkrbusy.locked():
                                    mutex_wrkrbusy.release()
                        else :
                            print("Length error")
                            self.ser.flush()
                            tgr_cmd= [81]  #L
                            "".join(map(chr, tgr_cmd))
                            self.uart.write(tgr_cmd)
                            time.sleep(0.5)
                            if mutex_wrkrbusy.locked():
                                mutex_wrkrbusy.release()
                            
                    else:
                        #raise NameError("CMD ERR: "+ read_buf[0]+'|'+ read_buf[1]+'|'+  read_buf[2]+'|'+  read_buf[3]+'|'+ read_buf[4]+'|'+  read_buf[5]+'|'+  read_buf[6])
                        print("Serial QR command responce exception 1:")
                        print(e)
                        tgr_cmd= [81]  #Q
                        "".join(map(chr, tgr_cmd))
                        self.uart.write(tgr_cmd)
                        #raise NameError("CMD ERR: "+read_buf.hex())
                except Exception as e:
                    
                    print("Serial QR command responce exception 2:")
                    print(e)
                    time.sleep(8)
                    try :
                        self.ser = serial.Serial('/dev/qrscanner', baudrate=115200, timeout=5,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS
                                    )
                    except Exception as e:
                        print("Ser. init:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                        print(e)
                        self.signals.error_signal.emit('Inbuilt QR Reader not found! - '+str(e),'In-built QR Reader error')
                        time.sleep(255)
                        sys.exit()
                    tgr_cmd= [81]  #Q
                    "".join(map(chr, tgr_cmd))
                    self.uart.write(tgr_cmd)
                if mutex_wrkrbusy.locked():
                    mutex_wrkrbusy.release()
            except Exception as e:
                print("Serial QR loop exception:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                if mutex_wrkrbusy.locked():
                    mutex_wrkrbusy.release()
                self.signals.error_signal.emit("Serial QR loop exception:"+str(e),'In-built QR Reader error')
                if str(e)=="read failed: device reports readiness to read but returned no data (device disconnected or multiple access on port?)":
                    time.sleep(3)
                else:
                    time.sleep(255)
                sys.exit() 

class TimerThreadSignals(QObject):
    update_time=pyqtSignal()
    update_jigdetails=pyqtSignal()
    update_jigip=pyqtSignal()
    error_signal=pyqtSignal(str,str)

class TimerThread(QRunnable):
    def __init__(self, ui_in):
        super(TimerThread, self).__init__()
        self.signals = TimerThreadSignals() 
        self.uin=ui_in
    def run(self):
        global synch_serialthread
        self.signals.update_time.emit()
        self.signals.update_jigdetails.emit()
        self.signals.update_jigip.emit()
        loop2=1
        loop=0
        time.sleep(1)
        now=datetime.now()
        if now.year < 2021 or now.year > 2029:
            time.sleep(5)
            now=datetime.now()
            if now.year < 2021 or now.year > 2029:
                error_msg="Wrong date/time:"+datetime.now().strftime("%d/%m/%Y-%H:%M:%S")+"\nEnsure WiFi is connected and restart jig"
                self.signals.error_signal.emit(error_msg, 'Time/date error!')
                time.sleep(255)
                sys.exit()
        synch_serialthread=0
        while True:
            self.uin.qr_input.setFocus()
            time.sleep(2)
            loop+=1
            if loop==30:
                self.signals.update_time.emit()
                #print('rrr\n')
                loop2+=1
                loop=0;
                if loop2==5:
                    loop2=0
                    self.signals.update_jigdetails.emit()
                    self.signals.update_jigip.emit()
          
class WorkerSignals(QObject):
    error_signal=pyqtSignal(str,str)
    change_value_matrix=pyqtSignal(str)
    change_value_cartridge=pyqtSignal(str)
    change_value_count=pyqtSignal(str)
    change_acceptvalue_count=pyqtSignal(str)
    change_rejectvalue_count=pyqtSignal(str)
    change_value_errors=pyqtSignal(str)           #self.update_time.emit()
            
class Worker(QRunnable):
    def __init__(self, mutex, cond,self_uart):
        global mutex_wrkrbusy
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.mtx = mutex
        self.cond = cond
        self.running=True
        self.uart=self_uart
    def stop(self):
        self.running=False
        
        
    #def reset_clicked(self):   
    #    print("resetcount")
        #self.w.pushButton_2.clicked.connect(self.reset_clicked)   
        
        
    @pyqtSlot()
    def run(self):
        global line,cube,user, mutex_wrkrbusy
        global text
        prev_cat='-'
        prev_matrix='-'
        matrix='-'
        #count=0
        serial=0
        accno=0
        rejno=0
        #self.setupUi(self)
        #self.pushButton_2.clicked.connect(self.reset_clicked)
        
        self.matrix_db = sqlite3.connect('/SCANNER/scanner.db')
        with open("/SCANNER/cat", "r") as f2:
            f2.seek(0)
            cursor0 = self.matrix_db.cursor()
            cursor0.execute('''SELECT SEQ from sqlite_sequence WHERE name='cartridge';''')
            count=int(cursor0.fetchone()[0])-int(f2.read())
            self.signals.change_value_count.emit(str(count))
        with open("/SCANNER/matrix.txt", "r") as f:
            f.seek(0)
            prev_matrix=matrix = f.read()
            self.signals.change_value_matrix.emit(matrix)
            
        with open('/SCANNER/Acc.csv') as f3:
            sacc = mmap.mmap(f3.fileno(), 0, access=mmap.ACCESS_READ)
            #if s.find(b'PAS12211702610') != -1:
            #    print('True')
            
        with open('/SCANNER/Rej.csv') as f3:
            srej = mmap.mmap(f3.fileno(), 0, access=mmap.ACCESS_READ)
            #if s.find(b'PAS12211702610') != -1:
            #    print('True')
                       
        while self.running:
            try:
                
                self.mtx.lock()
                #self.signals.change_value_count.emit("44")
                if mutex_wrkrbusy.locked():
                    mutex_wrkrbusy.release()
                self.cond.wait(self.mtx)
                mutex_wrkrbusy.acquire(blocking=False)
                self.mtx.unlock()
                #self.signals.change_value_count.emit("11")
                qr=text
                if qr[0] == matrixux.qr_id:
                    if qr == prev_matrix:
                        self.signals.change_value_errors.emit("Already scanned")
                        continue
                    #current_datetime=datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
                    count=0
                    with open("/SCANNER/cat", "w") as fc:
                        cursor4 = self.matrix_db.cursor()#
                        cursor4.execute('''SELECT SEQ from sqlite_sequence WHERE name='cartridge';''')
                        fc.write(str(cursor4.fetchone()[0])) 
                        cursor4.close()
                    prev_matrix=qr
                    if matrixux.qr_id =='M':
                        matrix=qr
                    else:
                        matrix=qr[1:]
                    with open("/SCANNER/matrix.txt", "w") as f:
                        f.seek(0)
                        f.write(matrix)
                    ####api
                    self.signals.change_value_count.emit(str(count))
                    self.signals.change_value_matrix.emit(matrix)
                    continue 
                else: 
                    if len(qr) < 10:
                        self.signals.change_value_cartridge.emit('QR LENGTH ERROR') 
                        print ("Len error:"+qr)
                        continue
                    cursor5=self.matrix_db.cursor()
                    cursor5.execute('''SELECT EXISTS(SELECT * FROM (SELECT * FROM cartridge ORDER BY SERIAL DESC LIMIT 50) WHERE CARTRIDGE="'''+qr+'''" LIMIT 1);''')
                    repetQr=cursor5.fetchone()[0]
                    #print(repetQr)
                    cursor5.close()
                    if repetQr==1:
                        #print ("Dup:"+qr)
                        continue
                        
                    if sacc.find(bytes(qr,'UTF-8')) != -1: 
                        self.signals.change_acceptvalue_count.emit(str(accno))
                        accno+=1
                        tgr_cmd= [65] #A
                        "".join(map(chr, tgr_cmd))
                        self.uart.write(tgr_cmd)
                    
                    elif srej.find(bytes(qr,'UTF-8')) != -1:                          
                        self.signals.change_rejectvalue_count.emit(str(rejno))
                        rejno+=1
                        tgr_cmd= [82]  #R
                        "".join(map(chr, tgr_cmd))
                        self.uart.write(tgr_cmd)
                    
                    else:
                        tgr_cmd= [78] #N
                        "".join(map(chr, tgr_cmd))
                        self.uart.write(tgr_cmd)
                        self.signals.change_rejectvalue_count.emit(str(rejno))
                        rejno+=1
                        #self.ui.CARTRIDGE_COUNT_2.setText(text)
                     
                        
                        cursor2=self.matrix_db.cursor()
                        count+=1
                        current_datetime=datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
                        sqlite_insert_with_param=str('''INSERT INTO cartridge VALUES ( ?, ?, ?, ?, ?, ?, ?);''')
                        data_tuple = (None,current_datetime,line,cube,matrix,qr,1)
                        cursor2.execute(sqlite_insert_with_param, data_tuple)
                        cursor2.close()
                        
                        self.signals.change_value_cartridge.emit(qr)
                        self.signals.change_value_count.emit(str(count))
                        #self.signals.change_value_count.emit("22")
                        cursor3=self.matrix_db.cursor()
                        cursor3.execute("SELECT  max(rowid) FROM cartridge")
                        MaxRowNo = int(cursor3.fetchone()[0])
                        cursor3.execute("SELECT  min(rowid) FROM cartridge")
                        MinRowNo = int(cursor3.fetchone()[0])
                            
                        if((MaxRowNo-MinRowNo)>500000) :
                            cursor3.execute("Delete from cartridge where rowid="+str(MinRowNo))  
                        cursor3.close()
                        self.matrix_db.commit()
                        
                        tgr_cmd= [65] #A
                        "".join(map(chr, tgr_cmd))
                        self.uart.write(tgr_cmd)
                        
                    #self.signals.change_value_count.emit("33")
            except Exception as e:
                self.signals.change_value_cartridge.emit('** ERROR **')
                print("Exception:"+datetime.now().strftime("%Y/%m/%d-%H:%M:%S"))
                print(e)
                tgr_cmd= [76] #A
                "".join(map(chr, tgr_cmd))
                self.uart.write(tgr_cmd)
                if mutex_wrkrbusy.locked():
                    mutex_wrkrbusy.release()
                self.signals.error_signal.emit("Worker exception:"+str(e),'Data logging error!')
                time.sleep(255)
                sys.exit()
        self.matrix_db.commit()
        self.matrix_db.close()
        

  


if __name__ == "__main__":
    import sys   
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = matrix_gui()
    MainWindow.show()
    sys.exit(app.exec_())
