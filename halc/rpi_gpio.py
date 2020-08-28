from . import hal
import sys,logging,time
try: import RPi.GPIO as GPIO
except:logging.debug("GPio Lib not installed")
class rpiGPIO(hal.GPIOActor):
    def __init__(self, id, parent=None):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(0,GPIO.IN)
            GPIO.input(0)
            hal.GPIOActor.__init__(self,id,parent)
        except:
            pass
    def setup(self,port,direction):
        try:
            pin = self.getPin(port)
            if direction == 'in':
                GPIO.setup(pin,GPIO.IN)
            if direction == 'out':
                GPIO.setup(pin,GPIO.OUT)
            if direction == 'tristate':
                GPIO.setup(pin,GPIO.IN)
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False
    def output(self,port,val):
        try:
            pin = self.getPin(port)
            if val > 0:
                GPIO.output(pin,GPIO.HIGH)
            else:
                GPIO.output(pin,GPIO.LOW)
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False
    def input(self,port):
        try:
            pin = self.getPin(port)
            return GPIO.input(pin)
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False