import logging,time,threading
Devices = []
class Module:
    """ Base Module Class, all other halc Classes are an Module
    """
    def find(self,id=None,typ=None,Name=None):
        """ With the find function you can search for Devices/Modules that are Childs of this Module

        just call it with an hardware id of the Module (mac adress, usb vid/pid ...) or an Name (can be set on your own some modules may support names that are avalible in the hardware (e.g. eeprom))
        or an device typ/class
        """
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
    """ Base class for all Sensors
    """
    def __str__(self):
        return Module.__str__(self)
class Actor(Module):
    """Base class for all Actors
    """
    def __str__(self):
        return Module.__str__(self)
class Interface(Sensor):
    """Base class for Interfaces 
    
    with Interfaces are Modules that makes it possible to access Busses or Hardware at example an RS232 Interface or an Sensor Plattform
    """
    def __init__(self, id, parent=None):
        Sensor.__init__(self,id,parent)
        self.Lock = threading.Lock()
    def __str__(self):
        return Module.__str__(self)
    def read(self,timeout=100):
        """ Reads an protocol from the Interface Protocol Que 
        """
        return None
    def write(self,prot):
        """ Sends an protocol 
        """
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
        """ Captures an single Frame
        """
        return read(self)
    def CaptureSequence(self,HandlerFunction):
        """Captures an sequence of images, the HandlerFunction is called for every ready frame
        """
        return False
    def Stop(self): 
        """ Stopps capturing the sequence
        """
        return False
class Camera(Video):pass
class Grabber(Video):pass
class Scanner(Video):pass
class ADC(Sensor):
    """Base class to access analog voltage
    """
    def Sample(self,Time):
        return False
class DAC(Actor):
    """Base class to generate analog voltages
    """
    def Output(self,Samples):
        return False
class AudioADC(ADC):
    def SetInputVolume(self,Volume,channel = None):
        """ Adjusts the input volume of the sound device
        """
        return False
    def SampleToWav(self,Filename,Time,SampleFormat='cd',Blocking=False):
        """Samples Time Seconds to an Wav file
        """
        return False
    def StopSampling(self):
        """immedialy stops the sampling
        """ 
        return False
class AudioDAC(DAC):
    def SetOutputVolume(self,Volume,channel = None):
        """ Adjusts the output volume of the sound device
        """
        return False
    def OutputFromWav(self,Filename):
        """ plays an wav file
        """
        return False
class Soundcard(AudioDAC,AudioADC):
    """An Audio Interface wich combines AudioDAC and AudioADC
    """
    pass
class VoltageSensor(ADC):
    def __init__(self, id,measurements=1, parent=None):
        self.measurements=measurements
        ADC.__init__(self,id,parent)
        self.Calibration = 0.0
    def Voltage(self,Port=1):
        return -1
    def Sample(self,Port=1):
        return self.Voltage(Port)
    def __str__(self):
        ret = Sensor.__str__(self)+' Voltage:'+str(self.Voltage())+' V'
        return  ret
class CurrentSensor(Sensor):
    def __init__(self, id, parent=None,measurements=1):
        Sensor.__init__(self,id,parent)
        self.measurements=measurements
        self.Calibration = 0.0
    def Current(self,Port=1):
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
    """ The MotorController drives Motors and Axes threaded 

    ```mermaid
    sequenceDiagram
        User->>Axis: Move(3)
        loop 3x
            MotorController-->>Axis: step()
            Axis->>Motor: step()
        end
        Axis->>MotorController: Done()
    ```
    """
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
    def add(self,Action):
        self.Actions.append(Action)
    def step(self):
        """ This function is the main function to work all actions, it is called by the controller loop. 
        
        When you set Autostart to False in the initialisation parameters, you can call step manually.
        """
        fst = 0.05
        if len(self.Actions) > 0:
            for Action in self.Actions:
                if Action.Done():
                    self.Actions.remove(Action)
                    del(Action)
                else:
                    st = Action.Step()
                    if st < fst:
                        fst = st
        time.sleep(fst)
    def run(self):
        """ runs the controller loop
        """
        while threading.main_thread().is_alive():
            self.step()
class MotorAction:
    """Base class to drive an motor
    """
    def __init__(self,Motor):
        self.Motor = Motor
        self.Depends = None
        self.Position = 0
        self.Value = None
        self.DoAbort = False
        self.ValuePerStep = 1
        self.Position = 0
    def Step(self,Steps=1.0):
        self.Position += Steps*self.ValuePerStep
    def Done(self):
        if self.Position is not None and self.Value is not None:
            if self.Value > 0:
                return self.Position >= self.Value
            else:
                return self.Position <= self.Value
        else:
            return self.DoAbort
    def Abort(self):
        self.DoAbort = True
class Movement(MotorAction):
    """Movement Class

    This class moves an specific way, or endless and keeps track to do it in an specific time or accelerate below the given value

    Speed: Endspeed in RPM (Max Motor RPM when None)
    Time: Time to Move (Endless when None)
    Acceleration: Accelerate Speed till Speed/maxRPM is reached
    """
    def __init__(self,Motor,Value=None,Speed=None,Time=None,Acceleration=None):
        MotorAction.__init__(self,Motor)
        self.Time = Time
        self.Value = Value
        if Value is not None and Value < 0 \
        or Speed is not None and Speed < 0:
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
    """is the Base class for an axis.
    
    ![](images/axis.jpg) 
    
    An axis describes an object that have an destination value and can have also an gearing and drives an motor to reach this destination vaue with an MotorAction
    """
    def __init__(self,id,Motor,MotorController,Transmission=1,parent=None):
        Actor.__init__(self,id,parent)
        self.Motor = Motor
        self.MotorController = MotorController
        self.Transmission = Transmission
        self.newPosition = 0
    def Move(self,Value=None,Speed=None,Time=None,Acceleration=None):
        """ with this function the User can set an Target position ti any time (even during movement)
        """
        self.newPosition = Value
        for Action in self.MotorController.Actions:
            if Action.Motor == self.Motor:
                Action.Abort()
        if Value is not None \
        and self.Position is not None:
            self.MotorController.add(Movement(self.Motor,Value-self.Position,Speed,Time,Acceleration))
        else:
            self.MotorController.add(Movement(self.Motor,None,Speed,Time,Acceleration))
    def Step(self,Steps,Direction):
        """ This function has to be called continously, normal that will be done threaded by MotorController bit it can be done also manually
        """
        self.Motor.Steps(Steps*self.Transmission,Direction)
    @property
    def Position(self):
        return self.Motor.Position*self.Transmission
    @Position.setter
    def Position(self, value):
        self.newPosition = value
class LinearAxis(Axis):
    def __init__(self,id,Motor,MotorController,Transmission=1,parent=None,Min=0,Max=None):
        Axis.__init__(self,id,Motor,MotorController,Transmission,parent)
        self.Min = Min
        self.Max = Max
        self.Overflow = False
    def Move(self,Value=None,Speed=None,Time=None,Acceleration=None):
        if self.Overflow:
            #TODO: calculate overflow
            Axis.Move(self,Value,Speed,Time,Acceleration)
        else:
            Axis.Move(self,Value,Speed,Time,Acceleration)
class RotationAxis(Axis):
    def __init__(self,id,Motor,MotorController,Transmission=1,parent=None,Min=0,Max=360):
        self.Offset = -((Max-Min)/2)
        LinearAxis.__init__(self,id,Motor,MotorController,Transmission,parent,self.Offset+Min,self.Offset+Max)
        self.Overflow = True
    def Move(self,Value=None,Speed=None,Time=None,Acceleration=None):
        if Value is not None:
            LinearAxis.Move(self,Value+self.Offset,Speed,Time,Acceleration)
        else:
            LinearAxis.Move(self,None,Speed,Time,Acceleration)
    def Rotate(self,Value,Speed=None,Time=None,Acceleration=None):
        Move(self,Value,Speed,Time,Acceleration)
    @property
    def Position(self):
        return Axis.Position-(self.Max-self.Min)
    @Position.setter
    def Position(self, value):
        self.newPosition = value+(self.Max-self.Min)
class Motor(Actor):
    """ Base class to drive an Motor
    """
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
    """Makes GPIO Pins accessable

    You can set Names for every Pin and access it per Name or Pin Number
    """
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
class BusController(Module):
    def up(self): pass
    def down(self): pass
class NetworkInterface(BusController):
    """ Basic Network Interface class
    """
    def addAddress(self,address,pefixlen): pass
class NetworkWifiInterface(NetworkInterface):
    """ Basic Network Wifi Interface Class
    """
    def Scan(self): 
        """ Scans for Wifi Networks
        """
    def Connect(self,ssid,passphrase=None): 
        """ Connect to an Wifi Network
        """
    def Disconnect(self): 
        """ Disconnect from actial connected Wiki Network
        """
class NetworkDevice(Module):
    """ Basic Network Device
    """
class NetworkSwitch(NetworkDevice):pass
class NetworkPOESwitch(NetworkSwitch):
    def SwitchPower(self,Port,On): 
        """ Switches POE on specified Port on/off
        """
class ABBusController(BusController): pass
Devices = Module('/')
def EnsureDevice(typ,name=None,WaitTime=0):
    """Function to ensure (wait) for an Device or fails if the Device is not there within an given amount of time
    """
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
    """ Shows the Device Tree as ASCII Tree
    """
    try: 
        import pptree
        pptree.print_tree(Devices,"Modules")
    except: pass