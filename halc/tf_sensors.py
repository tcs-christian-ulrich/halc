from . import hal
import time,threading,logging
try:
    from tinkerforge.ip_connection import IPConnection
    from tinkerforge.bricklet_voltage_current import BrickletVoltageCurrent
    from tinkerforge.bricklet_voltage_current_v2 import BrickletVoltageCurrentV2
    from tinkerforge.brick_master import BrickMaster
    from tinkerforge.brick_servo import BrickServo
    from tinkerforge.bricklet_io16 import BrickletIO16
    from tinkerforge.bricklet_io16_v2 import BrickletIO16V2
    from tinkerforge.bricklet_color import BrickletColor
    from tinkerforge.bricklet_color_v2 import BrickletColorV2
    from tinkerforge.bricklet_dual_relay import BrickletDualRelay
    from tinkerforge.bricklet_industrial_dual_relay import BrickletIndustrialDualRelay
    from tinkerforge.bricklet_industrial_quad_relay_v2 import BrickletIndustrialQuadRelayV2
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
        if devicetype == 13: return BrickMaster(id, ipcon)
        elif devicetype == 14: return BrickServo(id, ipcon)
        elif devicetype == 227: return BrickletVoltageCurrent(id, ipcon)
        elif devicetype == 2105: return BrickletVoltageCurrentV2(id, ipcon)
        elif devicetype == 28: return BrickletIO16(id, ipcon)
        elif devicetype == 2114: return BrickletIO16V2(id, ipcon)
        elif devicetype == 243: return BrickletColor(id, ipcon)
        elif devicetype == 2128: return BrickletColorV2(id, ipcon)
        elif devicetype == 26: return BrickletDualRelay(id, ipcon)
        elif devicetype == 284: return BrickletIndustrialDualRelay(id, ipcon)
        elif devicetype == 225: return BrickletIndustrialQuadRelay(id, ipcon)
        elif devicetype == 2102: return BrickletIndustrialQuadRelayV2(id, ipcon)
        else:
            print("Warning: DeviceType "+str(devicetype)+" not found")
            return None
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
    def Voltage(self,Port=1):
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
    def Current(self,Port=1,measurements=None):
        if not self.measurements:
            self.measurements = 1
        if measurements!=None:
            self.measurements=measurements
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
    def Color(self,Port=1):
        return self.Device.get_color()
class tfRelaisBricklet(hal.Relais):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Actor.__init__(self,id,parent)
        self.Device = tmp
        if self.Device.device_identifier == 26:
            self.Values = list(self.Device.get_state())
        else:
            self.Values = list(self.Device.get_value())
    def output(self,port,val):
        self.Values[self.getPin(port)] = val
        try:
            if self.Device.device_identifier == 26:
                self.Device.set_state(self.Values[0],self.Values[1])
            else:
                self.Device.set_value(self.Values)
            return True
        except:
            return False
    def __str__(self):
        try:
            ret = hal.Sensor.__str__(self)+' Status:'+str(self.Values)
            return  ret
        except:
            return hal.Sensor.__str__(self)
class tfIOBricklet(hal.GPIOActor):
    def __init__(self, id, devicetype, parent=None):
        tmp = findDeviceType(id,devicetype)
        hal.Actor.__init__(self,id,parent)
        self.Device = tmp
    def setup(self,port,direction):
        port = self.getPin(port)
        if direction == 'in':
            self.Device.set_configuration(port,'i',True)
        if direction == 'out':
            self.Device.set_configuration(port,'o',False)
        if direction == 'tristate':
            self.Device.set_configuration(port,'i',False)
    def output(self,port,val):
        port = self.getPin(port)
        if val:
            self.Device.set_selected_value(port,1)
        else:
            self.Device.set_selected_value(port,0)
    def input(self,port):
        port = self.getPin(port)
        return self.Device.get_value()[port]
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
        if device_identifier == 28\
        or device_identifier == 2114: #io16 Bricklet
            if hal.Devices.find(uid,hal.tfIOBricklet) == None:
                tfIOBricklet(uid,device_identifier,aParent)
        if device_identifier == 243 or device_identifier == 2128: #Color Bricklet
            if hal.Devices.find(uid,hal.ColorSensor) == None:
                tfColorSensor(uid,device_identifier,aParent)
        if device_identifier == 26\
        or device_identifier == 284\
        or device_identifier == 2102:
            if hal.Devices.find(uid,tfRelaisBricklet) == None:
                tfRelaisBricklet(uid,device_identifier,aParent)
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
        #11 	DC Brick
        #13 	Master Brick
        #14 	Servo Brick
        #15 	Stepper Brick
        #16 	IMU Brick
        #17 	RED Brick
        #18 	IMU Brick 2.0
        #19 	Silent Stepper Brick
        #21 	Ambient Light Bricklet
        #23 	Current12 Bricklet
        #24 	Current25 Bricklet
        #25 	Distance IR Bricklet
        #26 	Dual Relay Bricklet
        #27 	Humidity Bricklet
        #28 	IO-16 Bricklet
        #29 	IO-4 Bricklet
        #111 	HAT Brick
        #112 	HAT Zero Brick
        #210 	Joystick Bricklet
        #211 	LCD 16x2 Bricklet
        #212 	LCD 20x4 Bricklet
        #213 	Linear Poti Bricklet
        #214 	Piezo Buzzer Bricklet
        #215 	Rotary Poti Bricklet
        #216 	Temperature Bricklet
        #217 	Temperature IR Bricklet
        #218 	Voltage Bricklet
        #219 	Analog In Bricklet
        #220 	Analog Out Bricklet
        #221 	Barometer Bricklet
        #222 	GPS Bricklet
        #223 	Industrial Digital In 4 Bricklet
        #224 	Industrial Digital Out 4 Bricklet
        #225 	Industrial Quad Relay Bricklet
        #226 	PTC Bricklet
        #227 	Voltage/Current Bricklet
        #228 	Industrial Dual 0-20mA Bricklet
        #229 	Distance US Bricklet
        #230 	Dual Button Bricklet
        #231 	LED Strip Bricklet
        #232 	Moisture Bricklet
        #233 	Motion Detector Bricklet
        #234 	Multi Touch Bricklet
        #235 	Remote Switch Bricklet
        #236 	Rotary Encoder Bricklet
        #237 	Segment Display 4x7 Bricklet
        #238 	Sound Intensity Bricklet
        #239 	Tilt Bricklet
        #240 	Hall Effect Bricklet
        #241 	Line Bricklet
        #242 	Piezo Speaker Bricklet
        #243 	Color Bricklet
        #244 	Solid State Relay Bricklet
        #246 	NFC/RFID Bricklet
        #249 	Industrial Dual Analog In Bricklet
        #250 	Accelerometer Bricklet
        #251 	Analog In Bricklet 2.0
        #253 	Load Cell Bricklet
        #254 	RS232 Bricklet
        #255 	Laser Range Finder Bricklet
        #256 	Analog Out Bricklet 2.0
        #258 	Industrial Analog Out Bricklet
        #259 	Ambient Light Bricklet 2.0
        #260 	Dust Detector Bricklet
        #262 	CO2 Bricklet
        #263 	OLED 128x64 Bricklet
        #264 	OLED 64x48 Bricklet
        #265 	UV Light Bricklet
        #266 	Thermocouple Bricklet
        #267 	Motorized Linear Poti Bricklet
        #268 	Real-Time Clock Bricklet
        #270 	CAN Bricklet
        #271 	RGB LED Bricklet
        #272 	RGB LED Matrix Bricklet
        #276 	GPS Bricklet 2.0
        #277 	RS485 Bricklet
        #278 	Thermal Imaging Bricklet
        #279 	XMC1400 Breakout Bricklet
        #282 	RGB LED Button Bricklet
        #283 	Humidity Bricklet 2.0
        #284 	Industrial Dual Relay Bricklet
        #285 	DMX Bricklet
        #286 	NFC Bricklet
        #288 	Outdoor Weather Bricklet
        #289 	Remote Switch Bricklet 2.0
        #290 	Sound Pressure Level Bricklet
        #291 	Temperature IR Bricklet 2.0
        #292 	Motion Detector Bricklet 2.0
        #293 	Industrial Counter Bricklet
        #294 	Rotary Encoder Bricklet 2.0
        #295 	Analog In Bricklet 3.0
        #296 	Solid State Relay Bricklet 2.0
        #297 	Air Quality Bricklet
        #298 	LCD 128x64 Bricklet
        #299 	Distance US Bricklet 2.0
        #2100 	Industrial Digital In 4 Bricklet 2.0
        #2101 	PTC Bricklet 2.0
        #2102 	Industrial Quad Relay Bricklet 2.0
        #2103 	LED Strip Bricklet 2.0
        #2104 	Load Cell Bricklet 2.0
        #2105 	Voltage/Current Bricklet 2.0
        #2106 	Real-Time Clock Bricklet 2.0
        #2107 	CAN Bricklet 2.0
        #2108 	RS232 Bricklet 2.0
        #2109 	Thermocouple Bricklet 2.0
        #2110 	Particulate Matter Bricklet
        #2111 	IO-4 Bricklet 2.0
        #2112 	OLED 128x64 Bricklet 2.0
        #2113 	Temperature Bricklet 2.0
        #2114 	IO-16 Bricklet 2.0
        #2115 	Analog Out Bricklet 3.0
        #2116 	Industrial Analog Out Bricklet 2.0
        #2117 	Barometer Bricklet 2.0
        #2118 	UV Light Bricklet 2.0
        #2119 	Dual Button Bricklet 2.0
        #2120 	Industrial Dual 0-20mA Bricklet 2.0
        #2121 	Industrial Dual Analog In Bricklet 2.0
        #2122 	Isolator Bricklet
        #2123 	One Wire Bricklet
        #2124 	Industrial Digital Out 4 Bricklet 2.0
        #2125 	Distance IR Bricklet 2.0
        #2127 	RGB LED Bricklet 2.0
        #2128 	Color Bricklet 2.0
        #2129 	Multi Touch Bricklet 2.0
        #2130 	Accelerometer Bricklet 2.0
        #2131 	Ambient Light Bricklet 3.0
        #2132 	Hall Effect Bricklet 2.0
        #2137 	Segment Display 4x7 Bricklet 2.0
        #2138 	Joystick Bricklet 2.0
        #2139 	Linear Poti Bricklet 2.0
        #2140 	Rotary Poti Bricklet 2.0
        #2144 	Laser Range Finder Bricklet 2.0
        #2145 	Piezo Speaker Bricklet 2.0
        #2146 	E-Paper 296x128 Bricklet
        #2147 	CO2 Bricklet 2.0
        #2152 	Energy Monitor Bricklet
        #2153 	Compass Bricklet
        #2161 	IMU Bricklet 3.0          
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