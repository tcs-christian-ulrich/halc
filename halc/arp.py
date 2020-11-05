from . import hal
import threading,time,subprocess
class Enumerate(threading.Thread): 
    def run(self):
        global ip,iw
        while threading.main_thread().isAlive():
            try:
                for dev in hal.Devices.Modules:
                    try:
                        if isinstance(dev,hal.NetworkInterface)\
                        and dev.createdby == self:
                            dev.Found = False
                    except: pass
                try:
                    ap = subprocess.Popen(['arp','-an'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    ap.wait()
                    arp_entrys = ap.stdout.read().decode().split('\n')
                    for entry in arp_entrys:
                        try:
                            _,ip,_,mac,_,_,interface = entry.split()
                            ip = ip.replace('(','').replace(')','')
                            if subprocess.check_output(["ping", "-c", "1", ip]):
                                if sensors.Devices.find(mac) == None:
                                    pass
                                else:
                                    sensors.Devices.find(ip).Found = True
                        except: pass
                except: pass
                for dev in hal.Devices.Modules:
                    try:
                        if isinstance(dev,hal.NetworkInterface)\
                        and dev.createdby == self:
                            if dev.Found == False:
                                del(dev)
                    except: pass
            except: pass
            time.sleep(3)
enumerate = Enumerate() 
enumerate.start()        