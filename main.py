'''Main module'''
import sys
import time
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
    def __init__(self, parent=None, cnf=None):
        super(MainWindowCollaudo, self).__init__(parent)            # pylint: disable=super-with-arguments
        self.setupUi(self)
        self.comboPort.clear()
        for port in comports():
            self.comboPort.addItem(port.name)
        self.__setup__()

    def __setup__(self):
        self.btnSearchSerialPort.clicked.connect(self.__btnSearchCommclick__)
        self.btnTestComm.clicked.connect(self.__btnTestCommclick__)

    def __btnSearchCommclick__(self):
        self.comboPort.clear()
        for port in comports():
            self.comboPort.addItem(port.name)

    def __btnTestCommclick__(self):
        ser_port_mame = self.comboPort.currentText()
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

        ser.write("Test1\r\n".encode())
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()


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
