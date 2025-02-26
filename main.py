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
        self.btn_start_modem.clicked.connect(self.__btn_start_modem_click__)
        self.btn_start_modem_mqtt.clicked.connect(self.__btn_start_mqtt_click__)
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
        # idt_str = "0103164E02" #idx9900000001
        idt_str = "0203164E02" #idx9900000002
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
        # Centrale Lucio
        # cli_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDWTCCAkGgAwIBAgIUe5jM1v1Ps8cI4QMftNePg2eiLuAwDQYJKoZIhvcNAQEL\r\nBQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\r\nSW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTIzMDcwNzA4MjI1\r\nMVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\r\nZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMA3VKfjT6fDhvVOZWJ0\r\n1pjPT9oL4bKaVUs1tv4jvDD4J5DixEVaRei/Rctt7yvOcxI0eJ7AiA9hn8qZGoUX\r\n5Sk32Adh8ycNmFDU6WY+8W4FTkMCTgdT+4cj1clImtsNLkOcNWIFN1+aofMBRZ9W\r\nb+hqOGj8BHbHMFNIaYrCSr68tXPdDQ7YeCODeOPQ/G4u7OUrt8ChXyDpki2ry4Em\r\nBPWoNjbseOSiS4NYPKumq6jhKSs5LUe20ePxy29GMJkto+x1BskZOtVFU81c9xj6\r\nmIRL0r6VTEIoTJyZFyFXJv8Ow4vdzeSPp/KzTcmAYDLBdsfz8xs3LprhkIJu7Ur5\r\n7h8CAwEAAaNgMF4wHwYDVR0jBBgwFoAUIyuhjCHkrPCUa7woub0GF/HHvQAwHQYD\r\nVR0OBBYEFDq4Ob+pDT8FBHGpJcpUYC1oEN4jMAwGA1UdEwEB/wQCMAAwDgYDVR0P\r\nAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQA5AKi0o0X1w6D2NgCpMDi/C0tZ\r\nxT+gGqpIS7DGyo/1iLFuN0vcQ91Z5Uh+OfAuc1l9AhPRRINhcIk3XAXChOVlcTGE\r\na0XHCjV7O63E4MWN/jNEqf0F1rI61mdq9e3CFrlzDBNiIdj+l8VuptoNI38jdz98\r\nvNhXlC7qMPnWcwl9w8Ygy84ab5rTS8cwPgAnrLDkualZyGL1E0KmjowkIJFNgdJB\r\nDNXWvzR1Uj73nmY+Hgkt9jl7zsTiFLqhWQgKU2OfjPXJIQriww1veiSxkyBitb0Q\r\nJyot72zoowS37k0HF8x/GSS75U79sNEFgpFRLb0wQO+POJ4nwvNG5USbd54A\r\n-----END CERTIFICATE-----"
        # cli_key = "-----BEGIN RSA PRIVATE KEY-----\r\nMIIEogIBAAKCAQEAwDdUp+NPp8OG9U5lYnTWmM9P2gvhsppVSzW2/iO8MPgnkOLE\r\nRVpF6L9Fy23vK85zEjR4nsCID2GfypkahRflKTfYB2HzJw2YUNTpZj7xbgVOQwJO\r\nB1P7hyPVyUia2w0uQ5w1YgU3X5qh8wFFn1Zv6Go4aPwEdscwU0hpisJKvry1c90N\r\nDth4I4N449D8bi7s5Su3wKFfIOmSLavLgSYE9ag2Nux45KJLg1g8q6arqOEpKzkt\r\nR7bR4/HLb0YwmS2j7HUGyRk61UVTzVz3GPqYhEvSvpVMQihMnJkXIVcm/w7Di93N\r\n5I+n8rNNyYBgMsF2x/PzGzcumuGQgm7tSvnuHwIDAQABAoIBAE0Uoy0kOagz/6XV\r\nh1ChPAFReVseUqbVvwiHBNgLKoeUrAEs/ro1Bj3cnjeC4Vt20axmQEyhNq68XmDX\r\nXswqleoei9ICFIj/qaoYh3RKH3UYSZcTkIjdw8sgsrWiGP9o3LmeJcYmA1uiXfld\r\n9DZ+aigQmIh5L60WGan8Kt7LJUAxJ5DA0admcJUUSTrofxEbKRf3Aqo2A8JUWzLM\r\nuX8DbULDnvrxx48RqrEKe7CQUCcy5+cfbgKLwBYnVsS5U0IcQX+tAnp7WA0sl9zU\r\nVL64+3+DFc6vA7SwtDUjGbM3AWKXY6QPRK2LwjkNY4kBWtsivxCGKbky9Dj7Wzjc\r\nozb/SdkCgYEA+TAE8OxhODCa4SnYjOtylsqtUyr7jy3pRVQKTbsduW8847GrVRuO\r\n5IcdOxMYDesnK0VyX2A1CD2F7FJZEzhNgMTQwYDngd8FKDfueKUTJ0xe4iUo1M1L\r\nzkHW6/V/36fBfbYRDcBID5S6LcfmnBJlzEs+uJHyYqC9MlF1rPNfzCsCgYEAxXiW\r\nWGO6kbVvZ0X/i/K77N8fP2RIuBIrvUceeT8hucy4ZQhNAk66aXZZpNfD/7q3TWSA\r\njUOb/Afk6ZV1fLpFtZIVxRPZNjIBMfM8AFtII0bhwRNpErCjF3GWjPJ11be1omD8\r\n83Lf4uV49+O0+8Vwyr8NAtMZFdpBKPSNZkvUh90CgYBD0CCYHAv9CaUsf4HSH8UI\r\nalGu33SkK19fIZbIPpLBQxdz84bn218QrAB1ciXKq+L18KlGcV0dR/jpLiPVii31\r\nTBpvfpACFNpHbqk0JeBHgo4Txv8Mom3tzJcbkaziBbovZtvPPTOfId9k1BDbClqv\r\ntQ51lio7UvkJ94cpsPWyDwKBgAy00q/DUwj3LMDvbx8ZMmBuhvs0P72gZbIbNmnE\r\n1y22b5MIsrPYTwRkOiZyP8lfwVW4htEQLaRM+bzSAipRbhTd3oq82Tg0hYEqTo0T\r\nUpP6hqI+1n7+YLAsfex52X00Afr91KjxllhqPZttyoJ81OIm4vZwkOeoEJNLESIo\r\n9Pb9AoGAaW0MHv8TEKWMfiEZihGYXicm7TtLfJQ49fS9TpnpjUdmLIBxIbV8gwnV\r\nR96Wpvca0wkBCWiOprYXkji31a/OhUyNxNOosnTwfvCv0fH0mM2xIatwu/piraHU\r\ns0VbzdaVQZwHQ1NjdKrFOP1AbZfT06DQw6XQrbQjIM2uqxw/KtA=\r\n-----END RSA PRIVATE KEY-----"
       
        # idx9900000001
        # cli_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDWjCCAkKgAwIBAgIVAJPAotF7NJHbeJEasV2/DgyMJy7wMA0GCSqGSIb3DQEB\r\nCwUAME0xSzBJBgNVBAsMQkFtYXpvbiBXZWIgU2VydmljZXMgTz1BbWF6b24uY29t\r\nIEluYy4gTD1TZWF0dGxlIFNUPVdhc2hpbmd0b24gQz1VUzAeFw0yNTAyMjAxMjI1\r\nNTdaFw00OTEyMzEyMzU5NTlaMB4xHDAaBgNVBAMME0FXUyBJb1QgQ2VydGlmaWNh\r\ndGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDXKDvaVH7/iYhfydUg\r\nQHXit8h4X1d9IfX6/vdTyNrkN2qlMPirCM7pI0LAHQONqeb1XdU/qv6OOe99F274\r\ngRET63hzUJEdTizybKzJAY4MxqOTatwUvUZYOuv86gRLXJuUKHhNPGViPKmy1nCd\r\nFAUdzzSmZmEsBeEy3EJbK0pFDoXNWadLfcAqK5o8C/MGTqSicVtp906ieENrB56B\r\nUSayXRNehewMAHxKWRG2hCLsHMLXv8pg9tyjPQ7bCzXBYFvkkIvCqjOiuUEy5kEF\r\nARxgXkvK+N4NJQIUhgVKEcplghHHLUEClkxebfgetfn3N15c8/jTr+WyvlV+c7Ak\r\nn3jNAgMBAAGjYDBeMB8GA1UdIwQYMBaAFHUnHxtqzE5uNjDL1rY+u1suJRLnMB0G\r\nA1UdDgQWBBTYbYxBwlo6JdrxC7oR7OP0YdlwGDAMBgNVHRMBAf8EAjAAMA4GA1Ud\r\nDwEB/wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAQEAIelQwIJx60vNIvhZwPOwSIw7\r\nDXSQAnebz9Jfb2VVOD0L81tDbzyQskSS91gd2I6OSTKNLQRe0aPzhEnJNBzW3FNW\r\nM7FT+4H4q3pNrH0oSGtR0y4VUIEibVIXBlqepPvck81iJ4wgnLV+/IQr8140iP1h\r\n1V1LGlUEVFwM5kbDc7mhe94JjBK0sCfWf3eTW83Mdkru6trIRlX3keovDIy6XVkG\r\nxJqn0cnwwqV1G0R2jMvLOPQmUan1wvcvKCAddGT2hvhFXmQDZICqQt88BXY4DcG1\r\nMJ6LLTI/17JXlMbcxJA40S+TMDuO97VW5EItpUNzWgYolhNMPFclRg1xFnnjoQ==\r\n-----END CERTIFICATE-----"
        # cli_key = "-----BEGIN RSA PRIVATE KEY-----\r\nMIIEpQIBAAKCAQEA1yg72lR+/4mIX8nVIEB14rfIeF9XfSH1+v73U8ja5DdqpTD4\r\nqwjO6SNCwB0Djanm9V3VP6r+jjnvfRdu+IERE+t4c1CRHU4s8mysyQGODMajk2rc\r\nFL1GWDrr/OoES1yblCh4TTxlYjypstZwnRQFHc80pmZhLAXhMtxCWytKRQ6FzVmn\r\nS33AKiuaPAvzBk6konFbafdOonhDaweegVEmsl0TXoXsDAB8SlkRtoQi7BzC17/K\r\nYPbcoz0O2ws1wWBb5JCLwqozorlBMuZBBQEcYF5LyvjeDSUCFIYFShHKZYIRxy1B\r\nApZMXm34HrX59zdeXPP406/lsr5VfnOwJJ94zQIDAQABAoIBAQCurYyCQi1lG2yr\r\nj/pHF+5dZaYNDCLEhcjlwRBdZmlH9THQ8YRBn4IUxzrPK/8RiUnoFQknipTmNWUY\r\n4uiGOor56Cc/P77A0xIss0xIWMnR14dADPamo9Azm4qyJ+/am1H4JC8fTZRmACgp\r\n+G0vKezJecsd+WqUyiU+HJKG4AuJKba/T3MuqgNc02NTfl1Gh5dyzUyhfJRR4Q8l\r\natNmPmWfWP6Chl4cN8JNnkAg8NhFAP76gJ1O6XFrONTXZUmdBk5Arr5AVPxc/S42\r\n5aA+zhxGRUHJ+J2S7Pt5at5VhIn2wXnnOZI+8uMQPuZM9QHjlmgqaj+knxGMsno5\r\nBeNeQI9lAoGBAPWpB7Kukw/xw+57odDPYuKBLyafByVqAMGul1eOp09kX6SnkkH3\r\nO4MgOUmQaTyDXJNdYUqz/WumYCrFuXSvYjD2tDbC+nNvqQt7OyvK7pd4N3HGNsYK\r\n8OK4YfCiHzyWxzq9LxvYT9CnAcq/flav64aVGK4IaUTTScK0JBRmwHQLAoGBAOA2\r\niP7bGmXmQtzstvBoT4DlJW/R6eSH5rKzCsRlJtAabFrokA5HzLtIigTJNO2+EyOL\r\nGHNU+GaHhXQALW2XTrMTyfedL7xDjKLqot1HIPZs1AraaT+r0S3TbGbo6pf0DzHu\r\nvRywlHxOwqtJcbx1X6Ne+c0LQ5iuIPiQN7aM1DWHAoGBAKFkW1pYtuVSwJZ9QuIc\r\nXarRlFibQeairbyRJ3yui9zs5KkYLk6ITuDm2rwp0/mdk8R9JN4fQe7nb2aqYBz4\r\n3Fmuutb/YetVAIo6e7VZrUZ2BHcK8hFKPte0qyOcX0k/BcThZYG1qzo5fkPlauso\r\nyGOysHQlsoM1DNCN6OY+W1HhAoGBAJ6Bj0n0pW3iYeSDKDU+2O27kULC+IIKHWq5\r\nrmP3SoAWHgIKpUSjN7Yy6vfFMrjcBfW7sNZf/JenOQ4vze3K6OUqmT6HDice7f6C\r\nuA6M6V2sxB7EF2He2qt16w25nZc8/70CFQmCQAa9O1wSOOjNZYY+b4SocOowN7jh\r\nY7GXT7JjAoGAHyHPJq2ZxqWKgszFnL28Jk1CCTlyTk5ZzcfzdgUXm7Sd8HolJnz5\r\nSnwvZOhJZwOdgaHv5rnvD1YCgTqG2MlanBFJUpjkcPHNZ3uH/Mr14A++NsJumoQb\r\n3mih7WFAGny4bvwa+XhjzowKetQKc7fMeauv9BfXWV9L+8P+c14DqnM=\r\n-----END RSA PRIVATE KEY-----"
        
        # idx9900000002
        cli_cert = "-----BEGIN CERTIFICATE-----\r\nMIIDWjCCAkKgAwIBAgIVAJSSfKYNoY86TAA5IjbUsBq6tFjBMA0GCSqGSIb3DQEB\r\nCwUAME0xSzBJBgNVBAsMQkFtYXpvbiBXZWIgU2VydmljZXMgTz1BbWF6b24uY29t\r\nIEluYy4gTD1TZWF0dGxlIFNUPVdhc2hpbmd0b24gQz1VUzAeFw0yNTAyMjUwNzA1\r\nNDZaFw00OTEyMzEyMzU5NTlaMB4xHDAaBgNVBAMME0FXUyBJb1QgQ2VydGlmaWNh\r\ndGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC9zCccQBL8aBRS28ko\r\n1+jLBFPwt27VXQRzeOSxYOXoworTVcAnqCAuLfhbPPliTaP5mtTLpV0kggv7Av3z\r\nv5dSXXeik2sPxQuTL4EnuAosUsye5Kji2WQEZ5ytySO28epb3veW6sZYS2CbQfJL\r\n9BXiWNfjTAFI38JUtQ7Ihjje+cAxf0eUQkXdx/VHl97QdnNhoza/3nSJgusexL9m\r\nxmeX5GHuCOwE2K5xTHRySi6ypivFSIZ1UbpZn+ra3IsJfipeDxdlA5a7MFCpBrQc\r\nxSDOLxnAhrRX/FtOfoaSWFfy31x5vnOvls+YOrizqmyXTnKjPzuDC3MI7SSkCyYD\r\noNTnAgMBAAGjYDBeMB8GA1UdIwQYMBaAFCplrwo9yy44j/GW0Nt5jtMQNRP4MB0G\r\nA1UdDgQWBBRAMpvIkGAPxpBEHhN4f/M3FH5xtTAMBgNVHRMBAf8EAjAAMA4GA1Ud\r\nDwEB/wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAQEABHtmfvYy8/vHTtPLI3AIxxZm\r\nnVgpwfrHyuQ8v61BlljmOlBI8bChirbkqOxnzCqcQFj1FNrwVpW4BSEF9nxllVeS\r\n9CStiEf7LzuO6HHwVM672lsyHv2p8JYjtNPbejcG1W1bXXcWEuhMdkDbCejkvq34\r\nFvRp2lXMjvTJ5QSm3dqW9oEAODgeLdW6XhG3n3UCmlDkbQTqtK5cG+UqX7wgQhkD\r\nsW7j0wCKRuIbZ37l8e4dyRD7O65gDX/bNq66RZDxBE+TjZ69KDVx4ctwtjtFyIGV\r\nOZB+e4nO67WJnpUmsrPtToNA7jPqiXWxAqMAgctW1XL0PcsKGTQRJmGOci1NYA==\r\n-----END CERTIFICATE-----"
        cli_key = "-----BEGIN RSA PRIVATE KEY-----\r\nMIIEowIBAAKCAQEAvcwnHEAS/GgUUtvJKNfoywRT8Ldu1V0Ec3jksWDl6MKK01XA\r\nJ6ggLi34Wzz5Yk2j+ZrUy6VdJIIL+wL987+XUl13opNrD8ULky+BJ7gKLFLMnuSo\r\n4tlkBGecrckjtvHqW973lurGWEtgm0HyS/QV4ljX40wBSN/CVLUOyIY43vnAMX9H\r\nlEJF3cf1R5fe0HZzYaM2v950iYLrHsS/ZsZnl+Rh7gjsBNiucUx0ckousqYrxUiG\r\ndVG6WZ/q2tyLCX4qXg8XZQOWuzBQqQa0HMUgzi8ZwIa0V/xbTn6GklhX8t9ceb5z\r\nr5bPmDq4s6psl05yoz87gwtzCO0kpAsmA6DU5wIDAQABAoIBACiu+jM0CN3R8YlR\r\nU21N2rip1NRkfX1+0tVttJfRDXc3PErQtr/Jahx7/iCQkWRhACUg6zw71htdRPQp\r\nUAZPq0AciOhwcSKQOkryg9zftk6J8RKeMRVvQ+Et1Ifr9ZvhfzryMGBJMvr6LVsa\r\nZ7WgPJCoOp6eTCgyzpUZunGBU+93ejp5H6r6t4uMwBFLKAubyJf6vqVpnPIfoVnQ\r\ngHeo1U8Ho+XrKL6rcN00fVxUH8slW9IVmbht7R/7DKaVy5S/Ac9d0xkaIxAdaKUO\r\nyLtk02Mz/rYIDF2cg1gYZiaaI2xTSqUFPGf/XDY7AgdKlLN9j9judg5kicMXHd8Y\r\nYdnQNQECgYEA/JfYFwyqKe807m+LNLVuzpIxDiLdkdF/mC2wpJe6gKSej9etPH1m\r\nYlvgQV7RzYaRdenfqADfgx6G+QtdeOY0Y3mAW1xVwF82tsiOW52QKmNtzR3d4qvf\r\ncRMq+bkfNFgul48tjelCstPMBfQ1BeR2Rfcv/hstnWHfisTMU3QDWs0CgYEAwFt8\r\nuhOmpEX3sugsRo5sKNLiSwQRwPljMBKTVY67MShk9ylT1murvs4ufD7jKl64cl5M\r\nqbdeSaNUxzYVxiMYYb8+Nz4WSjfPvycvyNut/K9udUXRAyLplLedDuhhMXteteUH\r\nP+u6FfWTk8ykICxjfCciNeHXkB6U33HKwnwK1oMCgYEAt3nEaNm2MMekdx1mzF6N\r\nolbmcxI4R1cZi3yEtsnPmun4kxtipnGgEQoTlug9FUEOH8xFvU8FC8T83aG3v73X\r\nh/oVlkc3soh2wcZkQX/t3BxlAX0UUzXtE8GMkeA6Hld/YG+L82zgGe1mYVzFtwYA\r\nM0od/kHXnF4fdjkFAgle9nECgYBYBgWPiQqKxdHRttj7+JSaIdaYCWaubfDrwLRX\r\nRJd4qUl6qRjKWD8hc2xmQsjlTK8O9wQR7e1huTJEbwWLw+eWY1NvKCQ/Fkck7CO7\r\nwHtf1E+xrp801jcZbOScO86uPAxdJE8q+w4OmnBMBCte5bEo0SegjJZ+RuBNV983\r\nHFhBTQKBgECYLUtAC/yLQoiD1yRb7sOdwxn89lpp0+XxmBxYJIh6GkFk5M/C5Suc\r\ntErX2sbMStTTU4r8GPE2CQ84aXq3/pBF3P0fobADcgUFCTd209Iz5z1ax5X39iU/\r\nidrS9PTR871ZvkYVJVoe4NVmdkFJWfx2Fj1WldpgQ3MxdbspAl6f\r\n-----END RSA PRIVATE KEY-----"
        
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
        elif b"STMODM" in str_cmd :
            payload = recv_data[(idx_sep+1) : (idx_sep+1+32)]
            stat = payload[0 : payload.index(b'\x00')]
            str_stat = "0x" + stat.decode('utf-8')
            self.dut_int_stat = int(str_stat, 0)
            self.dut_status_signal.emit()
        elif b"STMQTT" in str_cmd :
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

    def __btn_start_modem_click__(self):
        self.__cfg_modem_sms_call__()

    def __btn_start_mqtt_click__(self):
        self.__cfg_modem_mqtt__()

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

    def __cfg_modem_sms_call__(self):
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
        cmd_str = b'{STMODM\x00\x00;'

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
    
    def __cfg_modem_mqtt__(self):
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
        cmd_str = b'{STMQTT\x00\x00;'

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
