import threading
import subprocess
import time
import  os.path

class ProgramStatus:
    """Stato programmatore ST"""
    def __init__(self):
        self.fw_ok = False
        self.cli_ok = False
        self.target_ok = False
        self.target_programmed = False
        self.status_reset()
      
    def status_reset(self):
        """Reset status"""
        self.fw_ok = False
        self.cli_ok = False
        self.target_ok = False
        self.target_programmed = False

class ProgrammatoreSt:
    """Gestione programmatore ST Link utilizzando STLINK Utility CLI"""
    def __init__(self,ProgramUpdateStatus=None, ProgramEndOk=None, ProgramEndErr=None):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        print("Init")

        # callback di ricezione
        self.ProgramEndOk = self.NullFunction
        self.ProgramEndErr= self.NullFunction
        self.ProgramUpdateStatus = self.NullFunction

        self.current_error="nessuno"

        self.file_path=""
        self.stlinkpath=""
        if callable(ProgramUpdateStatus):
            self.ProgramUpdateStatus = ProgramUpdateStatus
        if callable(ProgramEndOk):
            self.ProgramEndOk = ProgramEndOk
        if callable(ProgramEndErr):
            self.ProgramEndErr = ProgramEndErr

        self.avvia_programmazione=0
        self.errore_code=""
        self.frequency_KHz = 125
        self.flash_address = 0x08000000
        self.serial=""
        # thread per la gestione messaggi ricevuti
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True  # Daemonize thread
        self.thread.start()

        self.stato_programmazione=ProgramStatus()
        #self.timeout_rx_timer = threading.Timer(0.002, self.RxTimeout)

    def Program(self,stlinkpath, file_fw_path, frequency_KHz, flash_address,serial="", rdp_level=0):
        """Avvio programmazione"""
        self.stlinkpath=stlinkpath
        self.file_path=file_fw_path
        self.avvia_programmazione=1
        self.frequency_KHz=frequency_KHz
        self.flash_address=flash_address
        self.serial=serial
        self.rdp_protection=rdp_level

    def micro_reset(self):
        """Reset micro"""
        print("Micro reset\n")
        comstr=""
        try:
            if self.serial == "":
                comstr = self.stlinkpath + ' -c port=SWD reset=HWrst'
            else:
                comstr = self.stlinkpath + ' -c port=SWD' + ' SN=' + str(self.serial) + " reset=HWrst'"
        except Exception as e:
            print("format. error:", e)
        print(comstr)
        res = subprocess.check_output(comstr)
        print(res)

    def set_readout_protection(self, level):
        """Set readout protection"""
        prl=self.get_readout_protection_level()
        if prl == -1:
            return 1

        if prl==level:
            return 0

        str_level = '0xAA'
        if level == 0:
            str_level = '0xAA'
        elif level == 1:
            str_level = '0xBB'

        try:
            print("serial", self.serial)
            print("\n set redout protection \n")
            if self.serial == "":
                comstr = self.stlinkpath + ' -c port=SWD ' + "reset=HWrst -OB RDP=" + str_level
            else:
                comstr = self.stlinkpath + ' -c port=SWD ' + 'SN=' + self.serial + \
                    " reset=HWrst -OB RDP=" + str_level
        except:
            return 1

        try:
            print(comstr)
            res = subprocess.check_output(comstr)
            print(res)
            return 0
        except:
            return 1

    def get_readout_protection_level(self):
        """Read option byte readout protection"""
        if self.serial == "":
            comstr = self.stlinkpath + ' -c port=SWD' + " reset=HWrst -ob displ"
        else:
            comstr = self.stlinkpath + ' -c port=SWD' + " SN=" + str(self.serial) + " reset=HWrst -ob displ"

        print("comm string:", comstr)
        res = subprocess.check_output(comstr)
        print(str(res))
        # res = res.decode("utf-8")
        s = res.split()
        print(s)
        if b'RDP' in s:
            rdp_idx = s.index(b'RDP')
            str_rdp = s[rdp_idx + 2]
            return str_rdp.decode("utf-8")
        return -1

    def list_of_all_stlink(self,stlinkpath):
        ser_list = []
        try:
            l = subprocess.check_output([stlinkpath, '--List'])
            l = l.decode("utf-8")
            l = l.split()
            for x in range(len(l)):
                if l[x] == "SN":
                    ser_list.append(l[x + 2])
        except:
            pass
        return ser_list


    def NullFunction(self, *args):
        pass

    def run(self):
        """ Method that runs forever """
        while True:
            if self.avvia_programmazione:
                self.avvia_programmazione=0
                self.stato_programmazione.status_reset()
                self.current_error = "nessuno"
                freq=' Freq='+str(self.frequency_KHz)
                #subprocess.check_output( [self.stlinkpath, '-c SWD ',freq])

                try:
                    subprocess.check_output([self.stlinkpath, '-version'])
                    self.stato_programmazione.cli_ok = True
                    self.ProgramUpdateStatus()
                except:
                    self.current_error="cli path errato, o software st link non installato"
                    print(self.current_error)
                    self.ProgramEndErr()
                    continue

                try:
                    if os.path.exists(self.file_path) ==False:
                        self.current_error = "file fw non presente o percorso errato"
                        print(self.current_error)
                        self.ProgramEndErr()
                        continue
                    elif not (self.file_path.endswith(".hex") or self.file_path.endswith(".bin")):
                        self.current_error = "file fw estensione non corretta solo .bin o .hex supportati"
                        print(self.current_error)
                        self.ProgramEndErr()
                        continue
                    else:
                        print(self.file_path)
                        self.stato_programmazione.fw_ok=True
                        self.ProgramUpdateStatus()

                except:
                    self.ProgramEndErr()
                    self.current_error = "file fw errore"
                    continue

                #check target and readout protection
                res = self.get_readout_protection_level()
                if res == -1:
                    self.current_error = "error no target"
                    print(self.current_error)
                    self.ProgramEndErr()
                    continue
                else: 
                    if res != '0xAA':
                        if self.set_readout_protection('0xAA'):
                            self.current_error = "error no target"
                            print(self.current_error)
                            self.ProgramEndErr()
                            continue

                self.stato_programmazione.target_ok = True
                self.ProgramUpdateStatus()

                try:
                    print("\nFirmware programming....\n")
                    if self.serial != "":
                        comstr = self.stlinkpath +" -c port=SWD " + "SN=" + str(self.serial) + \
                            " reset=HWrst -e all -w " + self.file_path + " -V"
                    else:
                        comstr = self.stlinkpath +" -c port=SWD  reset=HWrst -e all -w " + \
                            self.file_path + " -V"
                    print("com progr: ",comstr)
                    res=subprocess.check_output(comstr)
                    res = str(res)
                    print(res)
                    if "Error occured during program operation!" in res:
                        self.current_error = "error durante programmazione"
                        print(self.current_error)
                        self.ProgramUpdateStatus()
                        self.ProgramEndErr()
                        continue
                    else:
                        if self.set_readout_protection(self.rdp_protection):
                            self.current_error = "error rdp protection level not set"
                            print(self.current_error)
                            self.ProgramEndErr()
                            continue

                        #self.micro_reset()
                        self.stato_programmazione.target_programmed = True
                        self.ProgramUpdateStatus()
                        self.ProgramEndOk()
                        # print("micro reset")
                        # if self.serial != "":
                        #     comstr = self.stlinkpath + ' -c SWD ' + ' SN=' + str(self.serial) + " -Rst -Run"
                        #     res = subprocess.check_output(comstr)
                        #
                        # else:
                        #     comstr = self.stlinkpath + ' -c SWD ' + " -Rst -Run"
                        #     res = subprocess.check_output(comstr)
                        # res = str(res)
                        # print("res reset", res)
                        # continue

                except:
                    self.current_error = "error durante programmazione"
                    print(self.current_error)
                    self.ProgramUpdateStatus()
                    self.ProgramEndErr()
                    continue
            else:
                time.sleep(1)
