from . import hal
import time,threading,logging
try:
    from tinkerforge.ip_connection import IPConnection
    from tinkerforge.bricklet_voltage_current import BrickletVoltageCurrent
    from tinkerforge.bricklet_voltage_current_v2 import BrickletVoltageCurrentV2
    from tinkerforge.brick_master import BrickMaster
    from tinkerforge.brick_servo import BrickServo
    from tinkerforge.bricklet_io16 import BrickletIO16
    from tinkerforge.bricklet_color import BrickletColor
except:
    print("No tinkerforge Libs installed")
    exit
ipcon = None
def findDeviceType(id,devicetype):
    global ipcon
    tmp = hal.Devices.find(id)
    if tmp!=None:
        return tmp.Device
    else:
        if devicetype == 13:
            return BrickMaster(id, ipcon)
        elif devicetype == 14:
            return BrickServo(id, ipcon)
        elif devicetype == 227:
            return BrickletVoltageCurrent(id, ipcon)
        elif devicetype == 2105:
            return BrickletVoltageCurrentV2(uid, ipcon)
        elif devicetype == 100:
            return BrickletIO16(id, ipcon)
        elif devicetype == 243:
            return BrickletColor(id, ipcon)
        else:
            print("Warning: DeviceType "+str(devicetype)+" not found")
class tfMasterBrick(hal.Module):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Module.__init__(self,id,parent)
        self.Device = tmp
    def Reset(self):
        self.Device.reset()
class tfServoBrick(hal.Module):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Module.__init__(self,id,parent)
        self.Device = tmp
class tfServoActor(hal.ServoActor):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        tmp1 = hal.Devices.find(id)
        hal.ServoActor.__init__(self,id,tmp1)
        self.Device = tmp
        for i in range(7):
            self.Names[i]=i
            self.ServoBasePosition[i]=0
    def Power(self,servo,BasePosition=None,Velocity=65535,Period=14248,on=True):
        hal.ServoActor.Power(self,servo,BasePosition,Velocity,Period,on)
        try:
            self.Device.set_velocity(servo,Velocity)
            self.Device.set_period(servo,Period)
            if BasePosition!=None:#only change Position during Power on, when BasePosition is set
                self.Device.set_position(servo,self.ServoBasePosition[servo])
            if on:
                self.Device.enable(servo)
            else:
                self.Device.disable(servo)
            return (on==False) or self.Device.is_enabled(servo)
        except:
            return False
    def Position(self,servo,Position,Relative=True):
        try:
            if Relative:
                self.Device.set_position(servo,self.ServoBasePosition[servo]+Position)
            else:
                self.Device.set_position(servo,Position)
            return True
        except:
            return False
    def ActualPosition(self,servo,Relative=True):
        try:
            if Relative:
                return self.ServoBasePosition[servo]-self.Device.get_current_position(servo)
            else:
                return self.Device.get_current_position(servo)
        except:
            return False
    def OutputVoltage(self,val):
        try:
            self.Device.set_output_voltage(val)
            return True
        except:
            return False
class tfServoCurrentSensor(hal.CurrentSensor):
    def __init__(self, id, devicetype,measurements=8, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.CurrentSensor.__init__(self,id,measurements=measurements,parent=parent)
        self.Device = tmp
    def Current(self):
        max_curr = 0
        try:
            for x in range(self.measurements):
                max_curr = max_curr+self.Device.get_overall_current()
            av_curr = round(float(max_curr)/self.measurements,4)
            return float(av_curr-self.Calibration)
        except:
            return -1
class tfVoltageSensor(hal.VoltageSensor):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Sensor.__init__(self,id,parent)
        self.Calibration = 0.0
        self.Device = tmp
    def Voltage(self):
        return float((self.Device.get_voltage()/1000)-self.Calibration)
class tfCurrentSensor(hal.CurrentSensor):
    def __init__(self, id, devicetype, parent=None,measurements=25):
        tmp = findDeviceType(id,devicetype)
        self.measurements=1
        hal.CurrentSensor.__init__(self,id,parent,measurements)
        self.Device = tmp
        self.Device = tmp
        #                      4,1.1ms  ,332us
        self.Device.set_configuration(BrickletVoltageCurrent.AVERAGING_4,4      ,3    )
    def Current(self):
        if not self.measurements:
            self.measurements = 1
        try:
            max_curr = 0
            for x in range(self.measurements):
                max_curr = max_curr+self.Device.get_current()
        except:
            self.Device.set_configuration(BrickletVoltageCurrent.AVERAGING_4,4      ,3    )
            max_curr = 0
            for x in range(self.measurements):
                max_curr = max_curr+self.Device.get_current()
        av_curr = round(float(max_curr)/self.measurements,4)
        #print('Time:',(time.time() - start)*1000)# = ca50ms
        return float(av_curr-self.Calibration)
class tfColorSensor(hal.ColorSensor):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Sensor.__init__(self,id,parent)
        self.Device = tmp
    def Color(self):
        return self.Device.get_color()
def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version,device_identifier, enumeration_type):# Register incoming enumeration
   #print("cb_enumerate():",uid, connected_uid, position, hardware_version, firmware_version ,device_identifier)
   if enumeration_type == IPConnection.ENUMERATION_TYPE_DISCONNECTED:
      #print("cb_enumerate().Disconnected: " + str(enumeration_type) + " UID: " + uid+" DID: "+str(device_identifier))
      aSensor = hal.Devices.find(uid)
      if aSensor:
        del(aSensor)
      return
   if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
           enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
      #print("cb_enumerate().Connected Type: " + str(enumeration_type) + " UID: " + uid+" DID: "+str(device_identifier))
      aParent = hal.Devices.find(connected_uid)
      if aParent:
        if device_identifier == 227 or device_identifier == 2105: # voltage current brick
            if hal.Devices.find(uid,hal.VoltageSensor) == None:
                tfVoltageSensor(uid,device_identifier,aParent)
                tfCurrentSensor(uid,device_identifier,aParent)
        if device_identifier == 100: #io16 Bricklet
            if hal.Devices.find(uid,hal.IOPort) == None:
                tfIOPort(uid,device_identifier,aParent)
        if device_identifier == 243: #Color Bricklet
            if hal.Devices.find(uid,hal.ColorSensor) == None:
                tfColorSensor(uid,device_identifier,aParent)
      else:
        if device_identifier == 13: #Master
            if hal.Devices.find(uid,tfMasterBrick) == None:
                tfMasterBrick(uid,device_identifier)
        if device_identifier == 14: #Servo
            if hal.Devices.find(uid,tfServoBrick) == None:
                sb = tfServoBrick(uid,device_identifier)
                tfServoActor(uid,device_identifier,sb)
                sc = tfServoCurrentSensor(uid,device_identifier,parent=sb)
                sc.Name = 'servo'
# Register Enumerate Callback
class tfEnumerate(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
    def run(self):
        global ipcon
        isexception = False
        try:
            ipcon = IPConnection()
            if ipcon.get_connection_state()!=IPConnection.CONNECTION_STATE_CONNECTED:
                ipcon.connect("localhost", 4223)
                ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)
                ipcon.time_out = 0.5
            ipcon.enumerate()
            time.sleep(0.3)
        except:
            logging.debug("Tinkerforge:failed connecting to IP Connection")
            pass
enumerate = tfEnumerate() 
enumerate.start()
def deinit():
    ipcon.disconnect()
    enumerate.kill()
    del(ipcon)
