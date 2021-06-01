from . import hal
try:
    import cv2,threading,io,time,picamera,picamera.array,queue,logging
    import numpy as np
    class StreamingOutput(object):
        def __init__(self,resolution):
            self.resolution = resolution
            self.frame = None
            self.buffer = io.BytesIO()
            self.condition = threading.Condition()
        def write(self, buf):
            self.buffer.truncate()
            res = self.buffer.write(buf)
            with self.condition:
                self.buffer.seek(0)
                self.frame = picamera.array.bytes_to_rgb(self.buffer.getvalue(),self.resolution)
                self.condition.notify_all()
                #print('frame capture (%d)' % len(buf))
            return res
    class PICamera(hal.Camera):
        def __init__(self, port=-1, parent=None,Name=None):
            if port == -1:
                hal.Sensor.__init__(self,'default',parent)
            else:
                hal.Sensor.__init__(self,str(port),parent)
            self.Port = port
            self.Name = Name
            self.cam = None
        def read(self,CloseCapture = False):
            if self.cam is None:
                self.init_capture()
            with self.output.condition:
                self.output.condition.wait()
            if CloseCapture:
                self.unload()
            if self.logger.getEffectiveLevel() == logging.DEBUG:
                cv2.imwrite('__cap_.png', output.frame)
            return self.output.frame
        def init_capture(self,cam=1):
            self.cam = picamera.PiCamera()
            self.cam.start_preview()
            time.sleep(0.2)
            self.output = StreamingOutput(self.cam.resolution)
            self.init_start(cam)
        def init_start(self,cam=1):
            #splitter_port=cam,
            self.cam.start_recording(self.output, format='rgb')
        def unload(self):
            self.cam.stop_recording()
            del(self.cam)
            self.cam = None
        def setResolution(width,height):
            if self.cam is None:
                self.init_capture()
            self.cam.resolution = (width, height)
            self.init_start()
            return True
        def setFPS(FPS):
            if self.cam is None:
                self.init_capture()
            self.cam.framerate = FPS
            self.init_start()
            return True
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