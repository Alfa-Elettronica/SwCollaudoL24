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
import programmatore_cypress
from MainWindow import Ui_MainWindow



class MainWindowCollaudo(QtWidgets.QMainWindow, Ui_MainWindow):     # pylint: disable=c-extension-no-member
    ''' Gui class
    '''
    run_ser_thread = False
    ser_thread = None
    st_lint_main = None
    st_lint_gsm = None
    pr_cyp = None
    program_end_error_signal=pyqtSignal()
    program_update_status_signal = pyqtSignal()
    dut_status_signal = pyqtSignal()
    dut_int_stat = 0

    STLinkV3_SN = "003500253038511034333935"
    STLinkV2_SN = "48FF6D068680575139451867"

    # pythoncom.CoInitialize()

    def __init__(self, parent=None):
        super(MainWindowCollaudo, self).__init__(parent)            # pylint: disable=super-with-arguments
        self.setupUi(self)
        self.comboPort.clear()
        self.btnStopComm.setEnabled(False)
        self.__host_plat = platform.system()
        print("Collaudo mini centrale in esecuzione su: " + self.__host_plat)
        for port in comports():
            self.comboPort.addItem(port.name)
        self.__init_st_link_interface__()
        self.pr_cyp=programmatore_cypress.ProgrammatoreCypress()
        self.pr_cyp.end_program.connect(self.__end_fase_programmazione_cypress__)
        self.pr_cyp.program_bar.connect(self.__update_progress_bar_cypress__)
        self.__setup__()
        self.__search_stlinks__()

    def __setup__(self):
        self.btnSearchSerialPort.clicked.connect(self.__btn_search_comm_click__)
        self.btnTestComm.clicked.connect(self.__btn_test_comm_click__)
        self.btnStartComm.clicked.connect(self.__start_comm_thread__)
        self.btnStopComm.clicked.connect(self.stop_comm_thread)
        self.btn_program_main.clicked.connect(self.__program_main_micro_collaudo__)
        self.btn_program_main_def.clicked.connect(self.__program_main_micro_produzione__)
        self.btn_prog_micro_gsm.clicked.connect(self.__program_main_micro_gsm__)
        self.btn_wr_idt.clicked.connect(self.__write_idt__)
        self.btn_wr_cli.clicked.connect(self.__write_cli__)
        self.btn_wr_hw.clicked.connect(self.__write_hwv__)
        self.btn_wr_magic_num.clicked.connect(self.__write_magic_num__)
        self.btn_prog_cypress.clicked.connect(self.__start_fase_programmazione_cypress__)
        self.btn_wr_cert1.clicked.connect(self.__btn_wr_cert1_click__)
        self.btn_tx_cert1.clicked.connect(self.__btn_tx_cert1_click__)
        self.btn_tx_cert1_modem.clicked.connect(self.__btn_tx_cert1_to_modem_click__)
        self.btn_wr_cert2.clicked.connect(self.__btn_wr_cert2_click__)
        self.btn_tx_cert2.clicked.connect(self.__btn_tx_cert2_click__)
        self.btn_tx_cert2_modem.clicked.connect(self.__btn_tx_cert2_to_modem_click__)
        self.btn_wr_cert3.clicked.connect(self.__btn_wr_cert3_click__)
        self.btn_tx_cert3.clicked.connect(self.__btn_tx_cert3_click__)
        self.btn_tx_cert3_modem.clicked.connect(self.__btn_tx_cert3_to_modem_click__)
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

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
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

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
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

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
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

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
        return rcv
    

    def __wr_cert__(self, cert_type):
        cli_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDWTCCAkGgAwIBAgIUe5jM1v1Ps8cI4QMftNePg2eiLuAwDQYJKoZIhvcNAQEL\r\nBQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\r\nSW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTIzMDcwNzA4MjI1\r\nMVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\r\nZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMA3VKfjT6fDhvVOZWJ0\r\n1pjPT9oL4bKaVUs1tv4jvDD4J5DixEVaRei/Rctt7yvOcxI0eJ7AiA9hn8qZGoUX\r\n5Sk32Adh8ycNmFDU6WY+8W4FTkMCTgdT+4cj1clImtsNLkOcNWIFN1+aofMBRZ9W\r\nb+hqOGj8BHbHMFNIaYrCSr68tXPdDQ7YeCODeOPQ/G4u7OUrt8ChXyDpki2ry4Em\r\nBPWoNjbseOSiS4NYPKumq6jhKSs5LUe20ePxy29GMJkto+x1BskZOtVFU81c9xj6\r\nmIRL0r6VTEIoTJyZFyFXJv8Ow4vdzeSPp/KzTcmAYDLBdsfz8xs3LprhkIJu7Ur5\r\n7h8CAwEAAaNgMF4wHwYDVR0jBBgwFoAUIyuhjCHkrPCUa7woub0GF/HHvQAwHQYD\r\nVR0OBBYEFDq4Ob+pDT8FBHGpJcpUYC1oEN4jMAwGA1UdEwEB/wQCMAAwDgYDVR0P\r\nAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQA5AKi0o0X1w6D2NgCpMDi/C0tZ\r\nxT+gGqpIS7DGyo/1iLFuN0vcQ91Z5Uh+OfAuc1l9AhPRRINhcIk3XAXChOVlcTGE\r\na0XHCjV7O63E4MWN/jNEqf0F1rI61mdq9e3CFrlzDBNiIdj+l8VuptoNI38jdz98\r\nvNhXlC7qMPnWcwl9w8Ygy84ab5rTS8cwPgAnrLDkualZyGL1E0KmjowkIJFNgdJB\r\nDNXWvzR1Uj73nmY+Hgkt9jl7zsTiFLqhWQgKU2OfjPXJIQriww1veiSxkyBitb0Q\r\nJyot72zoowS37k0HF8x/GSS75U79sNEFgpFRLb0wQO+POJ4nwvNG5USbd54A\r\n-----END CERTIFICATE-----"
        # cli_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDaaaCAkGgAwIBAgIUe5jM1v1Ps8cI4QMftNePg2eiLuAwDQYJKoZIhvcNAQEL\r\nBQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\r\nSW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTIzMDcwNzA4MjI1\r\nMVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\r\nZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMA3VKfjT6fDhvVOZWJ0\r\n1pjPT9oL4bKaVUs1tv4jvDD4J5DixEVaRei/Rctt7yvOcxI0eJ7AiA9hn8qZGoUX\r\n5Sk32Adh8ycNmFDU6WY+8W4FTkMCTgdT+4cj1clImtsNLkOcNWIFN1+aofMBRZ9W\r\nb+hqOGj8BHbHMFNIaYrCSr68tXPdDQ7YeCODeOPQ/G4u7OUrt8ChXyDpki2ry4Em\r\nBPWoNjbseOSiS4NYPKumq6jhKSs5LUe20ePxy29GMJkto+x1BskZOtVFU81c9xj6\r\nmIRL0r6VTEIoTJyZFyFXJv8Ow4vdzeSPp/KzTcmAYDLBdsfz8xs3LprhkIJu7Ur5\r\n7h8CAwEAAaNgMF4wHwYDVR0jBBgwFoAUIyuhjCHkrPCUa7woub0GF/HHvQAwHQYD\r\nVR0OBBYEFDq4Ob+pDT8FBHGpJcpUYC1oEN4jMAwGA1UdEwEB/wQCMAAwDgYDVR0P\r\nAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQA5AKi0o0X1w6D2NgCpMDi/C0tZ\r\nxT+gGqpIS7DGyo/1iLFuN0vcQ91Z5Uh+OfAuc1l9AhPRRINhcIk3XAXChOVlcTGE\r\na0XHCjV7O63E4MWN/jNEqf0F1rI61mdq9e3CFrlzDBNiIdj+l8VuptoNI38jdz98\r\nvNhXlC7qMPnWcwl9w8Ygy84ab5rTS8cwPgAnrLDkualZyGL1E0KmjowkIJFNgdJB\r\nDNXWvzR1Uj73nmY+Hgkt9jl7zsTiFLqhWQgKU2OfjPXJIQriww1veiSxkyBitb0Q\r\nJyot72zoowS37k0HF8x/GSS75U79sNEFgpFRLb0wQO+POJ4nwvNG5USbd54A\r\n-----END CERTIFICATE-----"
        cli_key = "-----BEGIN RSA PRIVATE KEY-----\r\nMIIEogIBAAKCAQEAwDdUp+NPp8OG9U5lYnTWmM9P2gvhsppVSzW2/iO8MPgnkOLE\r\nRVpF6L9Fy23vK85zEjR4nsCID2GfypkahRflKTfYB2HzJw2YUNTpZj7xbgVOQwJO\r\nB1P7hyPVyUia2w0uQ5w1YgU3X5qh8wFFn1Zv6Go4aPwEdscwU0hpisJKvry1c90N\r\nDth4I4N449D8bi7s5Su3wKFfIOmSLavLgSYE9ag2Nux45KJLg1g8q6arqOEpKzkt\r\nR7bR4/HLb0YwmS2j7HUGyRk61UVTzVz3GPqYhEvSvpVMQihMnJkXIVcm/w7Di93N\r\n5I+n8rNNyYBgMsF2x/PzGzcumuGQgm7tSvnuHwIDAQABAoIBAE0Uoy0kOagz/6XV\r\nh1ChPAFReVseUqbVvwiHBNgLKoeUrAEs/ro1Bj3cnjeC4Vt20axmQEyhNq68XmDX\r\nXswqleoei9ICFIj/qaoYh3RKH3UYSZcTkIjdw8sgsrWiGP9o3LmeJcYmA1uiXfld\r\n9DZ+aigQmIh5L60WGan8Kt7LJUAxJ5DA0admcJUUSTrofxEbKRf3Aqo2A8JUWzLM\r\nuX8DbULDnvrxx48RqrEKe7CQUCcy5+cfbgKLwBYnVsS5U0IcQX+tAnp7WA0sl9zU\r\nVL64+3+DFc6vA7SwtDUjGbM3AWKXY6QPRK2LwjkNY4kBWtsivxCGKbky9Dj7Wzjc\r\nozb/SdkCgYEA+TAE8OxhODCa4SnYjOtylsqtUyr7jy3pRVQKTbsduW8847GrVRuO\r\n5IcdOxMYDesnK0VyX2A1CD2F7FJZEzhNgMTQwYDngd8FKDfueKUTJ0xe4iUo1M1L\r\nzkHW6/V/36fBfbYRDcBID5S6LcfmnBJlzEs+uJHyYqC9MlF1rPNfzCsCgYEAxXiW\r\nWGO6kbVvZ0X/i/K77N8fP2RIuBIrvUceeT8hucy4ZQhNAk66aXZZpNfD/7q3TWSA\r\njUOb/Afk6ZV1fLpFtZIVxRPZNjIBMfM8AFtII0bhwRNpErCjF3GWjPJ11be1omD8\r\n83Lf4uV49+O0+8Vwyr8NAtMZFdpBKPSNZkvUh90CgYBD0CCYHAv9CaUsf4HSH8UI\r\nalGu33SkK19fIZbIPpLBQxdz84bn218QrAB1ciXKq+L18KlGcV0dR/jpLiPVii31\r\nTBpvfpACFNpHbqk0JeBHgo4Txv8Mom3tzJcbkaziBbovZtvPPTOfId9k1BDbClqv\r\ntQ51lio7UvkJ94cpsPWyDwKBgAy00q/DUwj3LMDvbx8ZMmBuhvs0P72gZbIbNmnE\r\n1y22b5MIsrPYTwRkOiZyP8lfwVW4htEQLaRM+bzSAipRbhTd3oq82Tg0hYEqTo0T\r\nUpP6hqI+1n7+YLAsfex52X00Afr91KjxllhqPZttyoJ81OIm4vZwkOeoEJNLESIo\r\n9Pb9AoGAaW0MHv8TEKWMfiEZihGYXicm7TtLfJQ49fS9TpnpjUdmLIBxIbV8gwnV\r\nR96Wpvca0wkBCWiOprYXkji31a/OhUyNxNOosnTwfvCv0fH0mM2xIatwu/piraHU\r\ns0VbzdaVQZwHQ1NjdKrFOP1AbZfT06DQw6XQrbQjIM2uqxw/KtA=\r\n-----END RSA PRIVATE KEY-----"
        ca_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\r\nADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\r\nb24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\r\nMAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\r\nb3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\r\nca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\r\n9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\r\nIFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\r\nVOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\r\n93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\r\njgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\r\nAYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\r\nA4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\r\nU5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\r\nN+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\r\no/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\r\n5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\r\nrqXRfboQnoZsG4q5WTP468SQvvG5\r\n-----END CERTIFICATE-----\r\n"
        dw_cert = ""
        if(cert_type == 1) :
            dw_cert = cli_cert
        if(cert_type == 2) :
            dw_cert = cli_key
        if(cert_type == 3) :
            dw_cert = ca_cert
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

        idx_start = 0
        bytes_to_transfer = len(dw_cert)

        tx_size = 512
        while(bytes_to_transfer > 0):
            tx_size = min(tx_size, bytes_to_transfer)
            cert_str = dw_cert[idx_start : idx_start + tx_size]
            cert_b = bytearray()
            cert_b.extend(map(ord, cert_str))
            cmd_str = b'{WRCERT\x00\x00;' + cert_type.to_bytes(1, 'little') + idx_start.to_bytes(2, 'little') + tx_size.to_bytes(2, 'little')
            cmd_str = cmd_str + cert_b
            buff_crc = self.__calcola_crc16__(len(cmd_str), cmd_str)
            cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
            ser.write(cmd_str)
            # let's wait one second before reading output (let's give device time to answer)
            time.sleep(0.3)
            rcv = ser.read_all()      
            idx_start = idx_start + tx_size
            bytes_to_transfer = bytes_to_transfer - tx_size
            if len(rcv) != 0:
                if self.__decode_command__(rcv) == 0:
                    print(rcv)
                else :
                    print('Decode error')
            else :
                print('No response')
        
        ser.close()
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

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
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
            self.lbl_test_13.setText("Load GSM default ok")
        else :
            self.lbl_test_13.setText("Load GSM default ---")


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

        crch = recv_data[idx_start + 42].to_bytes(1)
        crcl = recv_data[idx_start + 43].to_bytes(1)
        buff_crc = self.__calcola_crc16__(42, recv_data)

        if (crch != buff_crc[0]) or (crcl != buff_crc[1]) :
            return -4

        str_cmd = recv_data[idx_start : (idx_start + 8)]

        if b"RDSTAT" in str_cmd :
            payload = recv_data[(idx_sep+1) : (idx_sep+1+32)]
            stat = payload[0 : payload.index(b'\x00')]
            str_stat = "0x" + stat.decode('utf-8')
            self.dut_int_stat = int(str_stat, 0)
            self.dut_status_signal.emit()
        elif b"LDCERT" in str_cmd :
            payload = recv_data[(idx_sep+1) : (idx_sep+1+32)]
            stat = payload[0 : payload.index(b'\x00')]
            str_stat = "0x" + stat.decode('utf-8')
            self.dut_int_stat = int(str_stat, 0)
            self.dut_status_signal.emit()
        elif b"STCERT" in str_cmd :
            payload = recv_data[(idx_sep+1) : (idx_sep+1+32)]
            stat = payload[0 : payload.index(b'\x00')]
            str_stat = "0x" + stat.decode('utf-8')
            self.dut_int_stat = int(str_stat, 0)
            self.dut_status_signal.emit()
        else :
            if not b"OK" in recv_data  :
                return -5

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

    def __btn_wr_cert1_click__(self):
        self.__wr_cert__(1)
 
    def __btn_tx_cert1_click__(self):
        self.__tx_cert__()

    def __btn_tx_cert1_to_modem_click__(self):
        self.__tx_cert_to_modem__()

    def __btn_wr_cert2_click__(self):
        self.__wr_cert__(2)
 
    def __btn_tx_cert2_click__(self):
        self.__tx_cert__()

    def __btn_tx_cert2_to_modem_click__(self):
        self.__tx_cert_to_modem__()

    def __btn_wr_cert3_click__(self):
        self.__wr_cert__(3)
 
    def __btn_tx_cert3_click__(self):
        self.__tx_cert__()

    def __btn_tx_cert3_to_modem_click__(self):
        self.__tx_cert_to_modem__()

    def __calcola_crc16__(self, b_len, buf):
        cy = int(0)
        cy2 = int(0)
        crch = int(255)
        crcl = int(255)
        if b_len < 65535 :
            for x in range(b_len):
                crcl = (buf[x]) ^ crcl
                for _ in range(8) :
                    cy = crch & 1
                    crch = crch // 2
                    cy2 = crcl & 1
                    crcl = (crcl // 2) + cy * 128
                    if cy2 == 1 :
                        crch = crch ^ 0xA0
                        crcl = crcl ^ 0x01
        return [crch.to_bytes(1), crcl.to_bytes(1)]

    def __calcola_crc16_recv__(self, b_len, buf):
        cy = int(0)
        cy2 = int(0)
        crch = int(255)
        crcl = int(255)
        if b_len < 65535 :
            for x in range(b_len):
                crcl = (buf[x]) ^ crcl
                for _ in range(8) :
                    cy = crch & 1
                    crch = crch // 2
                    cy2 = crcl & 1
                    crcl = (crcl // 2) + cy * 128
                    if cy2 == 1 :
                        crch = crch ^ 0xA0
                        crcl = crcl ^ 0x01
        return [crch, crcl]


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
            self.start_fase_programmazione()
        
    def ProgrammaStGsmEndError(self):
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
            self.start_fase_programmazione()

    def __tx_cert__(self):
        '''Avvio trasferimento certificato a uCm
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
        cmd_str = b'{LDCERT\x00\x00;'

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
        return rcv

    def __tx_cert_to_modem__(self):
        ser_port_name = ''
        if self.__host_plat == "Windows":
            ser_port_name = self.comboPort.currentText()
        else:
            ser_port_name = "/dev/" + self.comboPort.currentText()
        ser = serial.Serial(
            port=ser_port_name,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        if ser.isOpen():
            ser.close()
        ser.open()
        ser.isOpen()
        cmd_str = b'{STCERT\x00\x00;'

        while len(cmd_str) < 42 :
            cmd_str = cmd_str + b'\x00'

        buff_crc = self.__calcola_crc16__(42, cmd_str)
        cmd_str = cmd_str + buff_crc[0] + buff_crc[1] + b'}'
        ser.write(cmd_str)
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(0.3)
        rcv = ser.read_all()
        ser.close()
        if len(rcv) != 0:
            if self.__decode_command__(rcv) == 0:
                print(rcv)
            else :
                print('Decode error')
        else :
            print('No response')
        return rcv

    def __program_main_micro_collaudo__(self) :
        self.ProgrammaSt(MainMicro = True, FwCollaudo = True)

    def __program_main_micro_produzione__(self) :
        self.ProgrammaSt(MainMicro = True, FwCollaudo = False)

    def __program_main_micro_gsm__(self) :
        self.ProgrammaSt(MainMicro = False, FwCollaudo = False)

    def ProgrammaSt(self, MainMicro, FwCollaudo):
        '''Avvia programmazione micro'''

        if MainMicro :
            stlink_sn=self.STLinkV3_SN
            if FwCollaudo :
                fwpath = "collaudo_mini_centrale.hex"
            else :
                fwpath = "mini_centrale.hex"
        else :
            stlink_sn=self.STLinkV2_SN
            fwpath="ComModGsm.hex"
        self.st_lint_main.Program(
            'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe',
                                  fwpath, "8000", "0x8000000", stlink_sn, 0)

    def ProgrammaStUpdateStatus(self):
        '''Aggiornamento stato programmazione'''
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

    def __init_st_link_interface__(self):
        self.st_lint_main=ProgrammatoreSt(ProgramEndErr=self.program_end_error_signal.emit,
                                        ProgramUpdateStatus=self.program_update_status_signal.emit)
        self.program_end_error_signal.connect(self.ProgrammaStEndError)
        self.program_update_status_signal.connect(self.ProgrammaStUpdateStatus)

    def __search_stlinks__(self) :
        st_link_list = self.st_lint_main.list_of_all_stlink('C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe')
        print(st_link_list)

    def __end_fase_programmazione_cypress__(self, err):
        print("__end_fase_programmazione_cypress__" + err)

    def __update_progress_bar_cypress__(self, val:int):
        print(val)

    def __start_fase_programmazione_cypress__(self):
        '''Avvia programmazione micro tastiera'''
        print("start programmazione tastiera")
        self.pr_cyp.set_fw_path('C:\\Users\\donald.fontanelli\\Documents\\Progetti\\Collaudi\\VimacL24\\SwCollaudoL24\\fw_tastiera.hex')
        self.pr_cyp.start()


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
