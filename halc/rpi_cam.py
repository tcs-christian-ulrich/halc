from . import hal
try:
    from picamera import PiCamera
    import cv2
    import numpy as np
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
                self.cam.start_preview()
                time.sleep(2)
            stream = io.BytesIO()
            self.cam.capture(stream, format='jpeg')
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            image = cv2.imdecode(data, 1)
            # OpenCV returns an array with data in BGR order. If you want RGB instead
            # use the following...
            #image = image[:, :, ::-1]
            return image
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
except: print("picamera package needs to be installed !")