import sys
from os import path
import logging
import logging.handlers
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication                            # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QMessageBox                             # pylint: disable=no-name-in-module
from serial.tools.list_ports import comports
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

    def __btnSearchCommclick__(self):
        self.comboPort.clear()
        for port in comports():
            self.comboPort.addItem(port.name)

if __name__ == '__main__':
    filename = path.join(path.dirname(path.abspath(__file__)), 'LeonardoL24.log')
    logging.basicConfig(
        format='%(asctime)s:%(levelname)-9s: %(message)s',
        handlers=[logging.handlers.TimedRotatingFileHandler(filename=filename, when='W0', interval=4)],
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARN)
    logging.info('Application start')
    app = QApplication(sys.argv)
    form = MainWindowCollaudo()
    form.show()
    app.exec_()

