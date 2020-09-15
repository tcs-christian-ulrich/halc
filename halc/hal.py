import logging,time,threading
Devices = []
class Module:
    def find(self,id=None,typ=None,Name=None):
        for m in self.Modules:
            if  ((id is None) or (m._id==id) or (id in m._id))\
            and ((typ is None) or (isinstance(m,typ)))\
            and ((Name is None) or ((m.Name is not None) and ((m.Name == Name) or (Name in m.Name)))):
                return m
            else:
                a = m.find(id,typ,Name)
                if a!=None:
                    return a
        return None
    def __init__(self, id, parent=None):
        self._id = id
        self.Modules = []
        self.Device = None
        self.Name =None
        self.Found = True
        if parent == None:
            parent = Devices
        if parent:
            parent.Modules.append(self)
        self.logger = logging.getLogger(type(self).__name__)
    def __str__(self):
        if self.Name is not None:
            ret = self.Name+' ('+str(self._id)+')'
        else:
            ret = str(self._id)
        return  ret
class Sensor(Module):
    def __str__(self):
        return Module.__str__(self)
class Actor(Module):
    def __str__(self):
        return Module.__str__(self)
class Interface(Sensor):
    def __init__(self, id, parent=None):
        Sensor.__init__(self,id,parent)
        self.Lock = threading.Lock()
    def __str__(self):
        return Module.__str__(self)
    def read(self,timeout=100):
        return None
    def write(self,prot):
        return False
class Video(Sensor):
    """ Video Capturing Base Class
    Allows to capture single frames or sequences from an camera, grabber or other video source
    The CaptureSequence function starts capturing and calls HandlerFunction for every captured frame
    """
    def __str__(self):
        return Module.__str__(self)
        self.Image = None
    def read(self):
        return None
    def Capture(self):
        return read(self)
    def CaptureSequence(self,HandlerFunction): pass
    def Stop(self): pass
class Camera(Video):pass
class Grabber(Video):pass
class Scanner(Video):pass
class ADC(Sensor):
    def Sample(self,Time):
        return False
class DAC(Actor):
    def Output(self,Samples):
        return False
class AudioADC(ADC):
    def SetInputVolume(self,Volume,channel = None):
        return False
    def SampleToWav(self,Filename,Time,SampleFormat='cd',Blocking=False):
        return False
    def StopSampling(self):
        return False
class AudioDAC(DAC):
    def SetOutputVolume(self,Volume,channel = None):
        return False
    def OutputFromWav(self,Filename):
        return False
class AnalogAudioIO(AudioDAC,AudioADC): pass
class VoltageSensor(ADC):
    def __init__(self, id,measurements=1, parent=None):
        self.measurements=measurements
        ADC.__init__(self,id,parent)
        self.Calibration = 0.0
    def Voltage(self):
        return -1
    def Sample(self):
        return self.Voltage()
    def __str__(self):
        ret = Sensor.__str__(self)+' Voltage:'+str(self.Voltage())+' V'
        return  ret
class CurrentSensor(Sensor):
    def __init__(self, id, parent=None,measurements=1):
        Sensor.__init__(self,id,parent)
        self.measurements=measurements
        self.Calibration = 0.0
    def Current(self):
        return -1
    def __str__(self):
        ret = Sensor.__str__(self)+' Current:'+str(self.Current())+' mA'
        return  ret
class ColorSensor(Sensor):
    def Color(self):
        return 0,0,0,-1 #RGBA
    def __str__(self):
        r,g,b,a = self.Color()
        ret = str(self._id)+' Color:'+str(r)+','+str(g)+','+str(b)+','+str(a)+','+' RGBA'
        return  ret
class MotorController(threading.Thread):
    def __init__(self, id, parent=None, Autostart=True):
        Actor.__init__(self,id,parent)
        threading.Thread.__init__(self)
        self.Actions = []
        self._updating = False
        self._steps = 0
        self._step_time = 0.01
        if Autostart:
            self.start()
    def Clear(self):
        self.Actions = []
        self._steps = 0
    def BeginUpdate(self):
        self._updating = True
    def EndUpdate(self):
        self._updating = False
        self.Calculate()
    def add(self,Action):
        self.Actions.append(Action)
    def addAfter(self,Action):
        self.Actions.append(Action)
        Action.Depends = self.Actions[self.Actions.length()]
    def step(self):
        fst = 0.05
        if len(self.Actions) > 0:
            for Action in self.Actions:
                st = Action.Step()
                if Action.Done():
                    del(Action)
                if st < fst:
                    fst = st
        time.sleep(fst)
    def run(self):
        while threading.main_thread().is_alive():
            self.step()
class MotorAction:
    def __init__(self,Motor):
        self.Motor = Motor
        self.Depends = None
        self.Position = 0
        self.Value = None
        self.DoAbort = False
        self.ValuePerStep = 1
    def Step(self,Steps=1.0):
        self.Position += Steps*self.ValuePerStep
    def Done(self):
        if self.Position is not None:
            return self.Position > self.Value
        else:
            return self.DoAbort
    def Abort(self):
        self.DoAbort = True
class Movement(MotorAction):
    """
    Speed: Endspeed in RPM (Max Motor RPM when None)
    Time: Time to Move (Endless when None)
    Acceleration: Accelerate Speed till Speed/maxRPM is reached
    """
    def __init__(self,Motor,Value=None,Speed=None,Time=None,Acceleration=None):
        MotorAction.__init__(self,Motor)
        self.Time = Time
        self.Value = Value
        if Value < 0:
            self.Dir = self.Motor.ANTICLOCKWISE
        else:
            self.Dir = self.Motor.CLOCKWISE
        self.ValuePerStep = self.Motor.GradPerStep
        self.Acceleration = Acceleration
        self.Speed = Speed
    def Step(self,Steps=1.0):
        MotorAction.Step(self,Steps)
        if self.Acceleration is not None:
            self.Motor.Speed(self.Motor.Speed()*Acceleration)
        mt = self.Motor.Step(Steps,self.Dir)
        return mt # Step Time
class Axis(Actor):
    def __init__(self,id,Motor,MotorController,Transmission=1,parent=None):
        Actor.__init__(self,id,parent)
        self.Motor = Motor
        self.MotorController = MotorController
        self.Transmission = Transmission
        self.Position = 0
        self.newPosition = 0
    def Move(self,Value=None,Speed=None,Time=None,Acceleration=None):
        self.newPosition = Value
        for Action in self.MotorController.Actions:
            if Action.Motor == self.Motor:
                Action.Abort()
        self.MotorController.add(Movement(self.Motor,Value-self.Position,Speed,Time,Acceleration))
    def Step(self,Steps,Direction):
        self.Motor.Steps(Steps*Transmission,Direction)
        if Direction == self.Motor.CLOCKWISE:
            self.Position += Steps*Transmission
        else:
            self.Position -= Steps*Transmission
class LinearAxis(Axis):
    def __init__(self,id,Motor,MotorController,Transmission=1,parent=None,Min=0,Max=None):
        Axis.__init__(self,id,Motor,MotorController,Transmission,parent)
        self.Min = Min
        self.Max = Max
class RotationAxis(Axis):
    def __init__(self,Motor,MotorController,Transmission=1,parent=None,Min=0,Max=360):
        Axis.__init__(Motor,MotorController,Transmission,parent)
        self.Min = Min
        self.Max = Max
    def Rotate(self,Value):
        if self.Position+Value>self.Max:
            pass
class Motor(Actor):
    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    def __init__(self, id, parent=None):
        Actor.__init__(self,id,parent)
        self.IsMoving = False
    def Enable(self): pass
    def Disable(self): pass
class StepperMotor(Motor):
    def __init__(self, id, maxRPM=800, parent=None):
        Motor.__init__(self,id,parent)
        self.GradPerStep = 1.8
        self.maxRPM = maxRPM
        self.Speed(self.maxRPM)
    def Speed(self,NewSpeed=-1):
        self.StepTime = (60/NewSpeed)/(360/self.GradPerStep)
        return 1/(self.StepTime*360)
    def Step(self,Steps,Direction): pass
    def Rotate(self,Grad):
        if Grad < 0:
            return self.Step(round(-(Grad)/self.GradPerStep),0)
        else:
            return self.Step(round( (Grad)/self.GradPerStep),1)
class ServoActor(Motor):
    def __init__(self, id, parent=None):
        Motor.__init__(self,id,parent)
        self.ServoBasePosition = {}
        self.Names = {}
    def setName(self,port,Name):
        self.Names[Name] = port
    def getServo(self,port):
        if isinstance(port, str): 
            pin = self.Names[port]
        else:
            pin = port
        return pin
    def Power(self,servo,BasePosition=None,Velocity=65535,Period=14248,on=True):
        servo = self.getServo(servo)
        if BasePosition:
            self.ServoBasePosition[servo] = BasePosition
        return False
    def Position(self,Servo,Position,Relative=True):
        return False
    def ActualPosition(self,servo,Relative=True):
        return None
    def OutputVoltage(self,val):
        return False
    def DisableAll(self,Relative=False):
        for servo in self.Names:
            if abs(self.ActualPosition(servo,Relative))>100:
                self.Power(servo,on=True)
                self.Position(servo,0,Relative)
        There = False
        for servo in self.Names:
            while not There:
                There = True
                for servo in self.Names:
                    if abs(self.ActualPosition(servo,Relative))>100:
                        #print(servo,self.ActualPosition(servo,Relative))
                        There = False
                time.sleep(0.1)
        for servo in self.Names:
            self.Power(servo,on=False)
    def EnableAll(self,Relative=True):
        for servo in self.Names:
            if abs(self.ActualPosition(servo,Relative))>100:
                self.Power(servo,on=True)
                self.Position(servo,0,Relative)
        There = False
        for servo in self.Names:
            while not There:
                There = True
                for servo in self.Names:
                    if abs(self.ActualPosition(servo,Relative))>100:
                        #print(servo,self.ActualPosition(servo,Relative))
                        There = False
                time.sleep(0.1)
class GPIOActor(Actor):
    def __init__(self, id, parent=None):
        Actor.__init__(self,id,parent)
        self.Names = {}
    def setName(self,port,Name):
        self.Names[Name] = port
    def getPin(self,port):
        if isinstance(port, str): 
            pin = self.Names[port]
        else:
            pin = port
        return pin
    def setup(self,port,direction):
        if direction == 'in':
            pass
        if direction == 'out':
            pass
        if direction == 'tristate':
            pass
    def output(self,port,val):
        pass
    def input(self,port):
        return None
class Compass(Sensor): 
    def getMagnet():
        pass
    def getBearing():
        pass
    def Enable():
        pass
    def Disable():
        pass
class BusController(Module): pass
class IPInterface(BusController): pass
class IPPOEInterface(BusController):
    def SwitchBusOn(Port,On): pass
class IPWifiInterface(IPInterface):
    def Scan(self): pass
    def Connect(self,ssid,passphrase=None): pass
    def Disconnect(self): pass
class ABBusController(BusController): pass
Devices = Module('/')
def EnsureDevice(typ,name=None,WaitTime=0):
    WaitTime += 0.1
    FirstSearch = True
    while WaitTime>0:
        dev = Devices.find(name,typ)
        if dev is not None: break
        dev = Devices.find(None,typ,name)
        if dev is not None: break
        typname = str(typ)
        typname = typname.replace('\'','')
        typname = typname.replace('>','')
        while typname.find('.')>-1:
            typname = typname[typname.find('.')+1:]
        if FirstSearch == True:
            if name is None:
                logging.warning("**STEP 999 waiting for device "+typname)
            else:
                logging.warning("**STEP 999 waiting for device "+name)
            FirstSearch = False
        time.sleep(0.1)
        WaitTime-=0.1
    if dev == None:
        if name is None:
            if FirstSearch == False:
                logging.warning("**ERROR "+typname+" not found")
        else:
            if FirstSearch == False:
                logging.error("**ERROR "+name+" not found")
        return False
    if FirstSearch == False:
        logging.warning("**STEPEND OK")
    return True
def showTree():
    try: 
        import pptree
        pptree.print_tree(Devices,"Modules")
    except: pass