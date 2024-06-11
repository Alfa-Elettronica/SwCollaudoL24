import  time
import pythoncom
from PyQt5.QtCore import QRunnable, QThread, QThreadPool,pyqtSignal,QObject
from Cypress_PSOC4 import PSOC4
import os

class HelloWorldTask(QRunnable):
    def run(self):
        print ("Hello world from thread", QThread.currentThread())
        time.sleep(5)
        print("Hello world from thread", QThread.currentThread())
        time.sleep(5)
        print("Hello world from thread", QThread.currentThread())
        time.sleep(5)


class ProgrammatoreCypress( QThread):

    end_program=pyqtSignal(str)
    program_bar = pyqtSignal(int)


    def __init__(self, fwpath=""):
        super(ProgrammatoreCypress, self).__init__()
        self.fwpath=fwpath
        self.end_ok=False
    #     self.cypr = PSOC4()
        self.progr=False

    def set_fw_path(self,fwpath):
        self.fwpath = fwpath
    def start_prog(self,fwpath):
        self.fwpath = fwpath
        self.progr=True
    def run(self):
        self.progr=False
        self.end_ok = False
        str=""
        print("start prog")
        self.program_bar.emit(0)

        # #fwpath="C:\\Users\\lucio.delmissier\\Documents\python\\collaudo tastiera\\KEYB_cypress.hex"
        # #print(cypr.pp.HEX_ReadFile(self.fwpath))
        #
        # cypr.pp.HEX_ReadFile(self.fwpath)
        # print("last error: ", cypr.m_sLastError)
        #
        #
        # hResult = cypr.pp.HEX_ReadChipProtection()
        # print("last error: ", cypr.m_sLastError)
        # hr = hResult[0]
        # hex_chipProt = hResult[1]
        # m_sLastError = hResult[2]
        #
        # #print(hResult)
        # #print(hex_chipProt)
        # #print("prot ",hex_chipProt[0])
        #
        # print(cypr.OpenPort())
        # print("last error: ", cypr.m_sLastError)
        # self.program_bar.emit(10)

        # self.fwpath = "C:\\Users\\lucio.delmissier\\Documents\python\\collaudo tastiera\\KEYB_cypress.hex"
        # if os.path.exists(self.fwpath) == False:
        #     self.end_program.emit("file fw non presente o percorso errato")
        #     return
        # self.program_bar.emit(10)
        #
        # if self.cypr.OpenPort()==-1:
        #     self.end_program.emit("Nessun programmatore cypress collegato")
        #     return



        # try:
        #     self.cypr.OpenPort()
        #     print("porteee")
        # except:
        #     self.end_program.emit("Nessun programmatore cypress collegato")
        #     return
        # hr=self.cypr.ProgramAll(self.fwpath)
        # print(hr)
        # print("last error: ", self.cypr.m_sLastError)
        # if (self.cypr.SUCCEEDED(hr)):
        #     str = "Succeeded!"
        #     self.program_bar.emit(100)
        #     self.end_ok = True
        # else:
        #     str = "Failed! " + self.cypr.m_sLastError
        #     self.program_bar.emit(0)
        # print (str)

        #self.end_program.emit(str)
        pythoncom.CoInitialize()
        
        cypr = PSOC4()

        # cypr.OpenPort(
        # fwpath = "C:\\Users\\lucio.delmissier\\Documents\python\\collaudo tastiera\\KEYB_cypress.hex"
        fwpath = self.fwpath
        print(fwpath)
        hr=cypr.pp.HEX_ReadFile(fwpath)

        if hr[1]==-1:
            self.end_program.emit("Percorso o formato file firmware programmazione errato")
            return


        hResult = cypr.pp.HEX_ReadChipProtection()
        hr = hResult[0]
        hex_chipProt = hResult[1]
        m_sLastError = hResult[2]

        print(hex_chipProt)
        print("prot ", hex_chipProt[0])

        #print("porte  ", cypr.OpenPort())

        es_ports=cypr.OpenPort()
        if es_ports==-1:
             self.end_program.emit("Nessun programmatore cypress collegato")
             return
        self.program_bar.emit(10)
        hr = cypr.ProgramAll(fwpath)
        print(hr)

        print("last error: ", cypr.m_sLastError)

        if (cypr.SUCCEEDED(hr)):
            self.program_bar.emit(100)
            self.end_ok=True
            str = "Succeeded!"
        else:
            self.program_bar.emit(0)
            str = "Failed! " + cypr.m_sLastError
        print(str)
        self.end_program.emit(str)