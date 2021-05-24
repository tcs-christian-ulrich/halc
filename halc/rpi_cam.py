from . import hal
try:
    import cv2,threading,io,time,picamera,picamera.array
    import numpy as np
    class PICamera(hal.Camera):
        def __init__(self, port=-1, parent=None,Name=None):
            if port == -1:
                hal.Sensor.__init__(self,'default',parent)
            else:
                hal.Sensor.__init__(self,str(port),parent)
            self.Port = port
            self.Name = Name
            self.cam = None
        def capture(self,CloseCapture = False):
            if self.cam is None:
                self.cam = PiCamera()
                self.cam.start_preview()
                time.sleep(2)
            with picamera.array.PiRGBArray(self.cam) as stream:
                self.cam.capture(stream, format='bgr')
                image = stream.array
                return image
    class PIEnumerate(threading.Thread): 
        def __init__(self): 
            threading.Thread.__init__(self) 
        def run(self):
            while threading.main_thread().is_alive():
                for dev in hal.Devices.Modules:
                    if isinstance(dev,PICamera):
                        dev.Found = False
                for i in range(0,1):
                    try:
                        adev = hal.Devices.find(i,PICamera)
                        if adev == None:
                            cam = PICamera(i,Name='piCamera')
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
except BaseException as e: 
    print('picamera package needs to be installed ! ('+str(e)+'"')