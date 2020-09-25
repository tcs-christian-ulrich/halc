import os,sys,unittest,time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from halc import hal
class TestMotor(hal.StepperMotor):
    def __init__(self, id, parent=None):
        hal.StepperMotor.__init__(self, id, parent=None)
        self.Position = 0
    def Step(self,Steps,Direction):
        print("TestMotor.Step "+str(Direction))
        if Direction==0:
            self.Position += Steps*self.GradPerStep
        else:
            self.Position -= Steps*self.GradPerStep
        return 0 # minimal time to next step
class MotorTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('mc')
        self.motor = TestMotor('mot')
    def test_LinearMovement(self):
        self.mc.add(hal.Movement(self.motor,1))
        time.sleep(0.6)
        self.assertGreater(self.motor.Position,15)
    def test_LinearMovementBack(self):
        self.mc.add(hal.Movement(self.motor,-15))
        time.sleep(0.06)
        self.assertLess(self.motor.Position,1)
class MotorAxisTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('mc',Autostart=False)
        self.motor = TestMotor('mot')
        self.la = hal.LinearAxis('ax',self.motor,self.mc,Max=100)
    def _test_AbsouluteMovement(self):
        self.la.Move(9)
        for i in range(7):
            self.mc.step()
        self.assertEqual(self.motor.Position,9)
    def _test_LinearMovement(self):
        self.la.Move()
        for i in range(5):
            self.mc.step()
        self.assertEqual(self.motor.Position,9)
    def _test_LinearMovementBack(self):
        self.la.Move(Speed=-self.motor.maxRPM)
        for i in range(5):
            self.mc.step()
        self.assertEqual(self.motor.Position,-9)
if __name__ == '__main__':
    unittest.main()