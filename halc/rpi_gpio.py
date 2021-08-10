from . import hal
import sys,logging,time
try: import gpiozero
except:logging.debug("GPio Lib not installed")
class rpiGPIO(hal.GPIOActor):
    def __init__(self, id, parent=None):
        try:
            hal.GPIOActor.__init__(self,id,parent)
        except:
            pass
        self.Pins = {}
    def setup(self,port,direction):
        try:
            p = hal.GPIOActor.getPin(self,port)
            if str(p) in self.Pins:
                gpio = self.Pins[str(p)]
                gpio.close()
                self.Pins[str(p)] = None
            if direction == 'in':
                self.Pins[str(p)] = gpiozero.DigitalInputDevice(p)
            if direction == 'out':
                self.Pins[str(p)] = gpiozero.DigitalOutputDevice(p)
            if direction == 'tristate':
                self.Pins[str(p)] = gpiozero.DigitalInputDevice(p)
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False
    def output(self,port,val):
        try:
            pin = self.getPin(port)
            if val > 0:
                self.Pins[str(pin)].on()
            else:
                self.Pins[str(pin)].off()
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False
    def input(self,port):
        try:
            pin = self.getPin(port)
            return self.Pins[str(pin)].value()
        except BaseException as e:
            logging.debug("Exception:"+str(e))
            return False