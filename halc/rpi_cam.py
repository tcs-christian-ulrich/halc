from . import hal
try:from picamera import PiCamera
except: print("picamera package needs to be installed !")
class PICamera(hal.Camera):
    def __init__(self, port=-1, parent=None,Name=None):
        if port == -1:
            hal.Sensor.__init__(self,'default',parent)
        else:
            hal.Sensor.__init__(self,str(port),parent)
        self.Port = port
        self.Name = Name
    def read(self,CloseCapture = False):
        if self.cam is None:
            self.cam = picamera.PiCamera()
        return self.capture(self.Device,CloseCapture = CloseCapture)
class PIEnumerate(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
    def run(self):
        context = pyudev.Context()
        while threading.main_thread().is_alive():
            for dev in hal.Devices.Modules:
                if isinstance(dev,PICamera):
                    dev.Found = False
            for i in range(0,1):
                try:
                    adev = hal.Devices.find(i,PICamera)
                    if adev == None:
                        cam = MPCamera(i,Name=dev.get('ID_MODEL'))
                        else:
                            adev.Found = True
                except:
                    pass
            for dev in hal.Devices.Modules:
                if isinstance(dev,PICamera):
                    if dev.Found == False:
                        del(dev)
            time.sleep(3)
enumerate = PIEnumerate() 
enumerate.start()