'''Main module'''
import sys
import time
import platform
import threading
from os import path
import logging
import logging.handlers
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication                            # pylint: disable=no-name-in-module
from serial.tools.list_ports import comports
import serial
from MainWindow import Ui_MainWindow



class MainWindowCollaudo(QtWidgets.QMainWindow, Ui_MainWindow):     # pylint: disable=c-extension-no-member
    ''' Gui class
    '''
    run_ser_thread = False
    ser_thread = None

    def __init__(self, parent=None, cnf=None):
        super(MainWindowCollaudo, self).__init__(parent)            # pylint: disable=super-with-arguments
        self.setupUi(self)
        self.comboPort.clear()
        self.btnStopComm.setEnabled(False)
        self.__host_plat = platform.system()
        print("Collaudo mini centrale in esecuzione su: " + self.__host_plat)
        for port in comports():
            self.comboPort.addItem(port.name)
        self.__setup__()

    def __setup__(self):
        self.btnSearchSerialPort.clicked.connect(self.__btn_search_comm_click__)
        self.btnTestComm.clicked.connect(self.__btn_test_comm_click__)
        self.btnStartComm.clicked.connect(self.__start_comm_thread__)
        self.btnStopComm.clicked.connect(self.__stop_comm_thread__)

    def __read_status__(self):
        '''Lettura stato collaudo
        '''
        ser_port_mame = ''
        if self.__host_plat == "Windows":
            ser_port_mame = self.comboPort.currentText()
        else:
            ser_port_mame = "/dev/" + self.comboPort.currentText()
        ser = serial.Serial(
            port=ser_port_mame,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        if ser.isOpen():
            ser.close()
        ser.open()
        ser.isOpen()
        cmd_str = b'{RDSTAT\x00\x00;'
        for idx in range(32):
            cmd_str = cmd_str + b'\x00'
        cmd_str = cmd_str + b'\x32\x33}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        self.__decode_command__(rcv)
        return rcv

    def __decode_command__(self, recv_data):
        '''Decodifica dati ricevuti'''
        idx_start = recv_data.index(b'{')
        idx_stop = recv_data.index(b'}')
        idx_sep = recv_data.index(b';')

        if idx_start == -1:
            return -1

        if len(recv_data) < (idx_start + 45):
            return -2

        if idx_stop == -1:
            return -3

        str_cmd = recv_data[idx_start : (idx_start+8)]
        if b"RDSTAT" in str_cmd :
            payload = recv_data[(idx_sep+1) : (idx_sep+1+32)]
            stat = payload[0 : payload.index(b'\x00')]
            str_stat = "0x" + stat.decode('utf-8')
            int_stat = int(str_stat, 0)
            print(int_stat)

        return 0


    def __ser_thread_loop__(self):
        '''Loop thread seriale
        '''
        while self.run_ser_thread :
            self. __read_status__()
            time.sleep(1)

    def __start_comm_thread__(self):
        '''Avvia thread comunicazione seriale'''
        self.run_ser_thread = True
        self.btnStartComm.setEnabled(False)
        self.btnStopComm.setEnabled(True)
        self.ser_thread = threading.Thread(target=self.__ser_thread_loop__)
        self.ser_thread.start()

    def __stop_comm_thread__(self):
        '''Arresta thread comunicazione seriale'''
        self.run_ser_thread = False
        self.btnStartComm.setEnabled(True)
        self.btnStopComm.setEnabled(False)
        self.ser_thread.join(timeout=5)

    def __btn_search_comm_click__(self):
        '''Ricarica lista porte seriali'''
        self.comboPort.clear()
        for port in comports():
            self.comboPort.addItem(port.name)

    def __btn_test_comm_click__(self):
        self.__read_status__()


if __name__ == '__main__':
    filename = path.join(path.dirname(path.abspath(__file__)), 'LeonardoL24.log')
    logging.basicConfig(
        format='%(asctime)s:%(levelname)-9s: %(message)s',
        handlers=[logging.handlers.TimedRotatingFileHandler(filename=filename,
                                                             when='W0', interval=4)],
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARN)
    logging.info('Application start')
    app = QApplication(sys.argv)
    form = MainWindowCollaudo()
    form.show()
    app.exec_()
