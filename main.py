'''Main module'''
import sys
import time
import platform
import threading
import logging
import logging.handlers
from os import path
import serial
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox          # pylint: disable=no-name-in-module
from PyQt5.QtCore import pyqtSignal                            # pylint: disable=no-name-in-module
from serial.tools.list_ports import comports
from programmatore_st import ProgrammatoreSt
from MainWindow import Ui_MainWindow



class MainWindowCollaudo(QtWidgets.QMainWindow, Ui_MainWindow):     # pylint: disable=c-extension-no-member
    ''' Gui class
    '''
    run_ser_thread = False
    ser_thread = None
    st_lint_main = None
    programmazzione_fw_cl_run = False
    program_end_error_signal=pyqtSignal()
    program_update_status_signal = pyqtSignal()
    dut_status_signal = pyqtSignal()
    dut_int_stat = 0

    STLinkV3_SN = "003500253038511034333935"
    STLinkV2_SN = "48FF6D068680575139451867"
   

    def __init__(self, parent=None, cnf=None):
        super(MainWindowCollaudo, self).__init__(parent)            # pylint: disable=super-with-arguments
        self.setupUi(self)
        self.comboPort.clear()
        self.btnStopComm.setEnabled(False)
        self.__host_plat = platform.system()
        print("Collaudo mini centrale in esecuzione su: " + self.__host_plat)
        for port in comports():
            self.comboPort.addItem(port.name)
      
        self.__init_st_link_interface__()
        self.__setup__()
        self.__search_stlinks__()

    def __setup__(self):
        self.btnSearchSerialPort.clicked.connect(self.__btn_search_comm_click__)
        self.btnTestComm.clicked.connect(self.__btn_test_comm_click__)
        self.btnStartComm.clicked.connect(self.__start_comm_thread__)
        self.btnStopComm.clicked.connect(self.stop_comm_thread)
        self.btn_program_main.clicked.connect(self.__program_main_micro_collaudo__)
        self.btn_program_main_def.clicked.connect(self.__program_main_micro_produzione__)
        self.btn_wr_idt.clicked.connect(self.__write_idt__)
        self.btn_wr_cli.clicked.connect(self.__write_cli__)
        self.btn_wr_hw.clicked.connect(self.__write_hwv__)
        self.btn_wr_magic_num.clicked.connect(self.__write_magic_num__)
        self.dut_status_signal.connect(self.__update_dut_status_ui__)

    def __write_idt__(self):
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
        idt_str = "ABCDEF0405"
        idt_b = bytearray()
        idt_b.extend(map(ord, idt_str))
        cmd_str = b'{WRIDT\x00\x00\x00;' + idt_b

        while(len(cmd_str) < 42) :
            cmd_str = cmd_str + b'\x00'

        cmd_str = cmd_str + b'\x31\x32}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        if len(rcv) != 0:
            self.__decode_command__(rcv)
        return rcv

    def __write_magic_num__(self):
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
        num_str = "0xFE"
        num_b = bytearray()
        num_b.extend(map(ord, num_str))
        cmd_str = b'{WRMAG\x00\x00\x00;' + num_b

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        cmd_str = cmd_str + b'\x31\x32}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        if len(rcv) != 0:
            self.__decode_command__(rcv)
        return rcv

    def __write_cli__(self):
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
        cli_str = "0A"
        cli_b = bytearray()
        cli_b.extend(map(ord, cli_str))
        cmd_str = b'{WRCLI\x00\x00\x00;' + cli_b

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        cmd_str = cmd_str + b'\x31\x32}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        if len(rcv) != 0:
            self.__decode_command__(rcv)
        return rcv

    def __write_hwv__(self):
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
        ver_str = "0102"
        ver_b = bytearray()
        ver_b.extend(map(ord, ver_str))
        cmd_str = b'{WRHWV\x00\x00\x00;' + ver_b

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        cmd_str = cmd_str + b'\x39\x38}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        if len(rcv) != 0:
            self.__decode_command__(rcv)
        return rcv

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

        while(len(cmd_str) < 42) :
            cmd_str = cmd_str + b'\x00'

        cmd_str = cmd_str + b'\x32\x33}'

        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        print(rcv)
        ser.close()
        if len(rcv) != 0:
            self.__decode_command__(rcv)
        return rcv

    def __update_dut_status_ui__(self) :
        '''Aggiornamento interfaccia grafica'''
        if self.dut_int_stat & (1 << 0) :
            self.lbl_test_1.setText("Test keyboard ok")
        else :
            self.lbl_test_1.setText("Test keyboard ---")
        if self.dut_int_stat & (1 << 1) :
            self.lbl_test_2.setText("Test led ok")
        else :
            self.lbl_test_2.setText("Test led ---")
        if self.dut_int_stat & (1 << 2) :
            self.lbl_test_3.setText("Test back-light ok")
        else :
            self.lbl_test_3.setText("Test back-light ---")
        if self.dut_int_stat & (1 << 3) :
            self.lbl_test_4.setText("Test buzzer ok")
        else :
            self.lbl_test_4.setText("Test buzzer ---")
        if self.dut_int_stat & (1 << 4) :
            self.lbl_test_5.setText("Test tamper ok")
        else :
            self.lbl_test_5.setText("Test tamper ---")
        if self.dut_int_stat & (1 << 5) :
            self.lbl_test_6.setText("Test input ok")
        else :
            self.lbl_test_6.setText("Test input ---")
        if self.dut_int_stat & (1 << 6) :
            self.lbl_test_7.setText("Test power ok")
        else :
            self.lbl_test_7.setText("Test power ---")
        if self.dut_int_stat & (1 << 7) :
            self.lbl_test_8.setText("Test flash mem ok")
        else :
            self.lbl_test_8.setText("Test flash mem ---")
        if self.dut_int_stat & (1 << 8) :
            self.lbl_test_9.setText("Test eeprom mem ok")
        else :
            self.lbl_test_9.setText("Test eeprom mem ---")
        if self.dut_int_stat & (1 << 9) :
            self.lbl_test_10.setText("Test radio ok")
        else :
            self.lbl_test_10.setText("Test radio ---")
        if self.dut_int_stat & (1 << 10) :
            self.lbl_test_11.setText("Test usb ok")
        else :
            self.lbl_test_11.setText("Test usb ---")
        if self.dut_int_stat & (1 << 11) :
            self.lbl_test_12.setText("Test GSM ok")
        else :
            self.lbl_test_12.setText("Test GSM ---")
        if self.dut_int_stat & (1 << 12) :
            self.lbl_test_13.setText("GSM INIT ok")
        else :
            self.lbl_test_13.setText("GSM INIT ---")


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
            self.dut_int_stat = int(str_stat, 0)
            self.dut_status_signal.emit()

        return 0

    def __ser_thread_loop__(self):
        '''Loop thread seriale '''
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

    def stop_comm_thread(self):
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

    def ProgrammaStEndError(self):
        '''Gestione errore programmazione flash micro'''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText(self.st_lint_main.current_error)
        msg.setInformativeText(
            "Premere \"Ok\" per terminare collaudo scheda, \"Cancel\" per ripetere il test")
        msg.setWindowTitle("Error")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # msg.buttonClicked.connect(msgbtn)
        retval = msg.exec_()
        print("value of pressed message box button:", retval)
        if retval == 0x00000400:
            print("Error ret val 0x00000400")
        else:
            if self.programmazzione_fw_cl_run:
                self.start_fase_programmazione_fwcl()
                self.start_fase_programmazione()

    def __program_main_micro_collaudo__(self) :
        self.ProgrammaSt(MainMicro = True, FwCollaudo = True)

    def __program_main_micro_produzione__(self) :
        self.ProgrammaSt(MainMicro = True, FwCollaudo = False)

    def ProgrammaSt(self, MainMicro, FwCollaudo):
        '''Avvia programmazione micro'''
        self.programmazzione_fw_cl_run = False
        if MainMicro :
            if FwCollaudo :
                fwpath = "collaudo_mini_centrale.hex"
            else :
                fwpath = "mini_centrale.hex"
            stlink_sn=self.STLinkV3_SN
        else :
            fwpath="ComModGsm.hex"
            stlink_sn=self.STLinkV2_SN
        self.st_lint_main.Program('C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe',
                                  fwpath, "8000", "0x8000000", stlink_sn, 0)
      
    def ProgrammaStUpdateStatus(self):
        if self.st_lint_main.stato_programmazione.cli_ok:
            print("st.stato_programmazione.cli_ok")

        if self.st_lint_main.stato_programmazione.target_ok:
            print("st.stato_programmazione.target_ok")
            # self.form_programmazione.checkBox_targetok.setCheckState(True)
        if self.st_lint_main.stato_programmazione.target_programmed:
            print("st.stato_programmazione.target_programmed")
        else:
            print("end_fase_programmazione_fwcl()")
        if self.st_lint_main.stato_programmazione.fw_ok:
            print("st.stato_programmazione.fw_ok")

    def ProgrammaSt_fwcl(self):
        self.programmazzione_fw_cl_run=True
        self.st_lint_main.Program(self.Impostazioni["cli_st_path"],self.fwcl,self.Impostazioni["frequency"],self.Impostazioni["address_memory"],self.Impostazioni["st_ser"])
        print("programmazione fw collaudo")
        if not self.collaudo_manuale:
            self.pushButton_program.setDisabled(True)
            self.pushButton_program_fwcl.setDisabled(True)

    def __init_st_link_interface__(self):
        self.st_lint_main=ProgrammatoreSt(ProgramEndErr=self.program_end_error_signal.emit,
                                          ProgramUpdateStatus=self.program_update_status_signal.emit)
        self.program_end_error_signal.connect(self.ProgrammaStEndError)
        self.program_update_status_signal.connect(self.ProgrammaStUpdateStatus)
        self.programmazzione_fw_cl_run=False

    def __search_stlinks__(self) :
        st_link_list = self.st_lint_main.list_of_all_stlink('C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe')
        print(st_link_list)
        

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
    app.lastWindowClosed.connect(form.stop_comm_thread)
    form.show()
    app.exec_()
