from . import hal
import time,json,threading,numpy as np,os,logging,pyudev,usb.core,cv2
class MPCamera(hal.Grabber):
    def __init__(self, port=-1, parent=None,Name=None,width=768,height=576,fps=25,norm='PAL'):
        if port == -1:
            hal.Grabber.__init__(self,'default',parent)
        else:
            hal.Grabber.__init__(self,str(port),parent)
        self.Port = port
        self.Name = Name
        self.width = width
        self.height = height
        self.fps = fps
        self.norm = norm
    def capture(self,dev,CloseCapture = False):
        os.system("mplayer tv:// -tv driver=v4l2:device=/dev/video"+str(self.Port)+":norm="+self.norm+":width="+str(self.width)+":height="+str(self.height)+":fps="+str(self.fps)+" -hardframedrop -rawvideo pal -vf pp=lb -frames 1 -vo png")
        img = cv2.imread("00000001.png")
        if self.logger.getEffectiveLevel() < logging.DEBUG:
            os.remove("00000001.png")
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
                                cam = MPCamera(i,Name=dev.get('ID_MODEL'),width=768,height=576)
                            elif dev.get('ID_USB_DRIVER').lower() == 'uvcvideo':
                                cam = MPCamera(i,Name=dev.get('ID_MODEL'),width=720,height=480)
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