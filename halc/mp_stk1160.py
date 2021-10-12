from . import hal
import time,json,threading,numpy as np,os,logging,pyudev,usb.core,cv2
class MPCamera(hal.Grabber):
    def __init__(self, port=-1, parent=None,Name=None):
        if port == -1:
            hal.Grabber.__init__(self,'default',parent)
        else:
            hal.Grabber.__init__(self,str(port),parent)
        self.Port = port
        self.Name = Name
    def capture(self,dev,CloseCapture = False):
        os.system("mplayer tv:// -tv driver=v4l2:device=/dev/video"+str(self.Port)+":norm=PAL:width=768:height=576:fps=25 -hardframedrop -rawvideo pal -vf pp=lb -frames 1 -vo png")
        img = cv2.imread("00000001.png")
        if self.logger.getEffectiveLevel() < logging.DEBUG:
            os.remove("00000001.png")
        try:
            self.h,  self.w = img.shape[:2]
            img = cv2.resize(img,(1024,768))
        except:
            return False
        return img
    def read(self,CloseCapture = False):
        return self.capture(self.Device,CloseCapture = CloseCapture)
    def unload(self):
        pass
class mpEnumerate(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
    def exists(self,path):
        try:
            os.stat(path)
        except OSError:
            return False
        return True
    def run(self):
        context = pyudev.Context()
        while threading.main_thread().is_alive():
            for dev in hal.Devices.Modules:
                if isinstance(dev,MPCamera):
                    dev.Found = False
            for i in range(0,25):
                try:
                    dev = pyudev.Devices.from_device_file(context, '/dev/video'+str(i))
                    if dev is not None:
                        adev = hal.Devices.find('/dev/video'+str(i),hal.Video)
                        if adev == None:
                            if dev.get('ID_USB_DRIVER').lower() == 'stk1160':
                                cam = MPCamera(i,Name=dev.get('ID_MODEL'))
                        else:
                            adev.Found = True
                except:
                    pass
            for dev in hal.Devices.Modules:
                if isinstance(dev,MPCamera):
                    if dev.Found == False:
                        del(dev)
            time.sleep(2)
enumerate = mpEnumerate() 
enumerate.start()