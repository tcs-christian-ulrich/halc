import os,sys,unittest,time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from halc import hal
class TestMotor(hal.StepperMotor):
    def __init__(self, id, parent=None):
        hal.StepperMotor.__init__(self, id, parent=None)
        self.Position = 0
    def Step(self,Steps,Direction):
        if Direction>0:
            self.Position += Steps*self.GradPerStep
        else:
            self.Position -= Steps*self.GradPerStep
class MotorTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('0')
        self.motor = TestMotor('1')
    def test_LinearMovement(self):
        self.mc.add(hal.Movement(self.motor,5))
        time.sleep(0.2)
        self.assertLess(self.motor.Position,5)
if __name__ == '__main__':
    unittest.main()