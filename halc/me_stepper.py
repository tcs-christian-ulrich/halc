# Raspberry Pi Stepper Motor Driver Class
# Hardware 28BYJ-48 Stepper 
# Gear Reduction Ratio: 1/64 
# Step Torque Angle: 5.625 degrees /64
# 360/5.625 = 64
#
# Author : Bob Rathbone
# Site   : http://www.bobrathbone.com
# HAL Version: Christian Ulrich https://www.cu-tec.de

import sys,os,time,threading
from . import hal

# The stepper motor can be driven in different ways
# See http://en.wikipedia.org/wiki/Stepper_motor

# Full step drive (Maximum Torque)
Aout1=[1,1,0,0]
Aout2=[0,1,1,0]
Aout3=[0,0,1,1]
Aout4=[1,0,0,1]

# Wave drive (increase angular resolution)
Bout1=[1,0,0,0]
Bout2=[0,1,0,0]
Bout3=[0,0,1,0]
Bout4=[0,0,0,1]

# Half step drive ( Maximum angle minimum torque)
Cout1=[1,1,0,0,0,0,0,1]
Cout2=[0,1,1,1,0,0,0,0]
Cout3=[0,0,0,1,1,1,0,0]
Cout4=[0,0,0,0,0,1,1,1]

class M28BYJ48(hal.StepperMotor,threading.Thread):
    GEARING = 64
    STEPS = 8
    REVOLUTION = GEARING * STEPS
    NORMAL = 0.0025
    SLOW = NORMAL * 2
    running = False 
    position = 0

    def __init__(self,id, gpio, pin1, pin2, pin3, pin4,parent=None,UseThread=False):
        hal.StepperMotor.__init__(self,id,round(60/(self.NORMAL*self.REVOLUTION)),parent)
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3
        self.pin4 = pin4
        self.out1=[]
        self.out2=[]
        self.out3=[]
        self.out4=[]
        self._speed = self.NORMAL
        self.IsMoving = False
        self._steps = 0
        self.GPIO = gpio
        self.setFullStepDrive()
        self.GradPerStep = 360.0/self.REVOLUTION
        self.UseThread = UseThread
        if UseThread:
            threading.Thread.__init__(self)
    # Initialise GPIO pins for this motor
    def Enable(self):
        self.GPIO.setup(self.pin1,'out')
        self.GPIO.setup(self.pin2,'out')
        self.GPIO.setup(self.pin3,'out')
        self.GPIO.setup(self.pin4,'out')
        self.position=0
        if self.UseThread:
            self.start()
        return	
    # Reset (stop) motor
    def Disable(self):
        self.GPIO.output(self.pin1,0)
        self.GPIO.output(self.pin2,0)
        self.GPIO.output(self.pin3,0)
        self.GPIO.output(self.pin4,0)
        self.IsMoving = False
        return	
    # Turn the motor
    def Step(self,Steps,Direction):
        global CLOCKWISE
        self.IsMoving = True
        self._steps = Steps	
        self._direction = Direction	
        hal.StepperMotor.Step(self,Steps,Direction)
        return Steps*self._speed
    def run(self):
        while threading.main_thread().is_alive():
            if self._steps > 0:
                if self._direction == self.CLOCKWISE:
                    for pin in range(self._mrange):
                        self.GPIO.output(self.pin1,self.out1[pin])
                        self.GPIO.output(self.pin2,self.out2[pin])
                        self.GPIO.output(self.pin3,self.out3[pin])
                        self.GPIO.output(self.pin4,self.out4[pin])
                        time.sleep(self.speed)
                    self._incrementPosition()
                else:
                    for pin in reversed(range(self._mrange)):
                        self.GPIO.output(self.pin1,self.out1[pin])
                        self.GPIO.output(self.pin2,self.out2[pin])
                        self.GPIO.output(self.pin3,self.out3[pin])
                        self.GPIO.output(self.pin4,self.out4[pin])
                        time.sleep(self.speed)
                    self._decrementPosition()
                self._steps -= 1
            elif self.IsMoving:
                self.IsMoving = False
                self.Disable()
            else:
                time.sleep(0.05)
    def Stop(self):
        self._steps = 0
        return
    # Increment current position 
    def _incrementPosition(self):
        self.position += 1
        if self.position >= self.REVOLUTION:
            self.position -= self.REVOLUTION
        return self.position
    # Increment current position 
    def _decrementPosition(self):
        self.position -= 1
        if self.position < 0:
            self.position += self.REVOLUTION
        return self.position
    # Lock the motor (also keeps motor warm)
    def _lock(self):
        self.GPIO.output(self.pin1,1)
        self.GPIO.output(self.pin2,0)
        self.GPIO.output(self.pin3,0)
        self.GPIO.output(self.pin4,1)
        self.IsMoving = False
        return	

    # Set Full Step Drive
    def setFullStepDrive(self):
        global Aout1,Aout2,Aout3,Aout4
        self.out1 = Aout1
        self.out2 = Aout2
        self.out3 = Aout3
        self.out4 = Aout4
        self.speed = self.NORMAL
        self._mrange = len(self.out1)
        return

    # Set Half Step Drive
    def setHalfStepDrive(self):
        global Bout1,Bout2,Bout3,Bout4
        self.out1 = Bout1
        self.out2 = Bout2
        self.out3 = Bout3
        self.out4 = Bout4
        self.speed = self.NORMAL
        self._mrange = len(self.out1)
        return

    # Set Wave Drive
    def setWaveDrive(self):
        global Cout1,Cout2,Cout3,Cout4
        self.out1 = Cout1
        self.out2 = Cout2
        self.out3 = Cout3
        self.out4 = Cout4
        self.speed = self.NORMAL/3
        self._mrange = len(self.out1)
        return

    # Set speed of motor
    def setSpeed(self,speed):
        self.speed = speed
        return
