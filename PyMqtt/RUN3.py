# 핵심코드
# -------------------------------------------------------------------------------------
# * 변수, 필드
# MyWindow.t_time
# 총 가공시간
#
# MyWindow.OUTPUT
# 아두이노 아웃풋 값 { "Sec" : 0 or 1, "Total_Count" : 0 or 1}
#
# MyWindow.user_count
# 사용자가 직접 총 생산량을 설정한 값
#
# MyWindow.sub_time
# 1개의 완제품을 만드는데 걸리는 시간
#
# MyWindow.total_count
# 완제품 개수
#
# MyWindow.new_count_signal
# 아두이노에서 "Total_Count" 값이 1이나 0일때 저장함
#
# MyWindow.delay
# DB에 전송 할 때 지연 플레그
#
# MyWindow.count_flag
# 카운트 값이 들어왔을 때 True 시간값일 때는 False 둘 다 안들어올 때도 False
#
# MyWindow.ser
# 아두이노 시리얼 값을 불러오기 위한 객체
#
# MyWindow.conn
# 데이터베이스 연결 객체
#
# MyWindow.timer
# SerialWorker의 QThread객체를 담고있다
# QThread객체란 : 일반 쓰레드를 사용하거나 다른 쓰레드 사용시
#                 UI 창이 닫히고 계속 실행되는 현상이 나타남
#                 이를 해결할 수 있는 방법이 Qt에서 제공하는 QTrhead를 사용하는 것이다.
#
# MainWindow.timerVar, MainWindow.timerDB
# QTimer객체를 사용하여 일정 주기마다 어떠한 메소드를 실행하게 한다.
# QTimer객체란 : setInterval과 같은 역할을 하는 객체이다.
# ------------------------------------------------------------------------------------
# * 메소드
# MainWindow.count_reset - Line 130
# 초기화 버튼을 누르면 총 가공시간, 개당 가공시간, 총 카운트가 초기화된다.
#
# rerender - Line 146
# MainWindow.timerVar를 통해서 1초마다 한번씩 실행되며 카운트 신호 또는 시간 신호에 따라
# 카운트 신호는 카운트 값을 1 늘이고, 시간신호는 시간초를 1 늘인다.
# 만약 카운트 신호가 1 들어오면 쌓였던 sub_time의 값은 초기화된다.
#
# MainWindow._db_send - Line 179
# 1분마다 1번씩 DB에 총 가공시간, 총 생산수량을 INSERT하게 한다.
#
# MainWindow.DB_connection - Line 199
# DB에 연결하는 메소드이다.
#
# MainWindow.DB_connet_save - Line 221
# DB에 총 가공시간, 총 생산수량을 INSERT하게 한다.
#
# SerialWorker.run - Line 308
# 1초마다 아두이노 시리얼을 받는다.
# 받은 값은 MyWindow.OUTPUT에 저장하고 MyWindow.sub_time과 MyWindow.t_time은
# OUTPUT["Sec"]의 값을 더하고, 완제품이 나오면 MyWindow.total_count에
# OUTPUT["Total_Count"]값을 더한다.
# ------------------------------------------------------------------------------------

import sys
import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtGui import QFont
from PyQt5 import uic
from PyQt5.QtCore import QThread

import DBConncet as db
import GPIOArduiono as arduino
import QtTools as qt_tools
import Mqtt


# UI 파일 위치 변경
UI = uic.loadUiType("C:/Users/oct_sky_out/Desktop/HoamQt/Main.UI")[0]


class MyWindow(QMainWindow, QWidget, UI):
    def __init__(self):
        super().__init__()

        self.OUTPUT = {}

        self.t_time = 0
        self.sub_time = 0

        self.user_count = 0
        self.total_count = 0
        self.new_count_signal = 0
        self.count_flag = False

        self.delay = 0

        self.setupUi(self)
        font = QFont("은 굴림", 14)
        self.btn_reset.setFont(font)

        self.Pages_widget.setCurrentWidget(self.Monitor_1)

        self.ser = arduino.GpioArduino()

        # 아두이노 리눅스나 윈도우 환경 등 포트 번호 확인!
        self.ser.set_ardu_path("COM7")
        self.ser = self.ser.open_arduino()

        self.timer = SerialWorker(parent=self).start()

        self.timerVar = qt_tools.QtTools().set_interval_qt(1000, self.rerender)
        self.timerVar.start()

        self.timerDB = qt_tools.QtTools().set_interval_qt(1000, self._db_send)
        self.timerDB.start()

        self.tool = qt_tools.QtEventTools()

    def dial_value_changed(self):
        self.tool.set_text(self.dial_count_number, str(self.dial_count.value()))

    def dial_value_set(self):

        self.user_count = int(self.count.text()) + self.dial_count.value()

        self.tool.set_text(self.count, str(self.user_count))

    def count_reset(self):

        self.dial_count.setValue(0)
        self.tool.set_text(self.dial_count_number, str(self.dial_count.value()))

        self.tool.set_text(self.count, "0")
        self.user_count = 0
        self.total_count = 0

        self.t_time = 0
        self.sub_time = 0

        self.tool.set_text(self.hour, "00")
        self.tool.set_text(self.min, "00")
        self.tool.set_text(self.sec, "00")
        self.tool.set_text(self.t_hour, "00")
        self.tool.set_text(self.t_min, "00")
        self.tool.set_text(self.t_sec, "00")

    def rerender(self):
        if self.new_count_signal == 1:
            self.count_flag = True
            self.total_count += self.new_count_signal
            self.tool.set_text(self.count, str(self.total_count + self.user_count))
        else:
            #          self.sub_time += self.OUTPUT["Sec"]
            if self.count_flag:
                self.sub_time = 0
                self.tool.set_text(self.hour, "00")
                self.tool.set_text(self.min, "00")
                self.tool.set_text(self.sec, "00")
                self.count_flag = False

            sub_sec = self.tool.timespan_to_dict(self.sub_time)
            self.tool.set_text(self.hour, sub_sec["hour"])
            self.tool.set_text(self.min, sub_sec["min"])
            self.tool.set_text(self.sec, sub_sec["sec"])

        #        self.t_time += self.OUTPUT["Sec"]
        total_sec = self.tool.timespan_to_dict(self.t_time)
        self.tool.set_text(self.t_hour, total_sec["hour"])
        self.tool.set_text(self.t_min, total_sec["min"])
        self.tool.set_text(self.t_sec, total_sec["sec"])

    def _db_send(self):
        self.delay += 1

        if 60 == self.delay:
            self.DB_connet_save()
            self.delay = 0

    def DB_connet_save(self):
        try:
            sendData = {
                "time": f"""{self.hour.text()}{self.min.text()}{self.sec.text()}""",
                "count": self.count.text(),
            }
            Mqtt.device_id = 2
            Mqtt.single_publish(sendData=sendData)
        except Exception as err:
            print(
                """
                ----------------SAVE ERROR--------------------
                """
            )
            print(err)
            print(
                """
                ----------------------------------------------
                """
            )


class SerialWorker(QThread):
    def __init__(self, parent: MyWindow = None):
        super().__init__(parent)

    def run(self):
        while True:
            try:
                self.parent().OUTPUT = json.loads(self.parent().ser.readline().decode())
                # print(self.parent().OUTPUT)
                self.parent().t_time += self.parent().OUTPUT["Sec"]
                self.parent().sub_time += self.parent().OUTPUT["Sec"]

                self.parent().new_count_signal = self.parent().OUTPUT["Total_Count"]
                QApplication.processEvents()

                print(self.parent().OUTPUT["Total_Count"])
                print(self.parent().OUTPUT["Sec"])
                QThread.sleep(0.5)
            except:
                continue


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
