import os,sys,unittest,time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from halc import hal
class TestMotor(hal.StepperMotor):
    def __init__(self, id, parent=None):
        hal.StepperMotor.__init__(self, id, parent=None)
    def Step(self,Steps,Direction):
        #print("TestMotor.Step "+str(Direction))
        hal.StepperMotor.Step(self,Steps,Direction)
        return 0 # minimal time to next step
    def Enable(self):
        self.Enabled = True
    def Disable(self):
        self.Enabled = False
class MotorTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('mc')
        self.motor = TestMotor('mot')
    def test_directLinearMovement(self):
        mm = hal.Movement(self.motor,15)
        for i in range(15):
            mm.Step()
            if mm.Done():
                break
        self.assertGreater(self.motor.Position,15)
        self.assertTrue(mm.Done())
        self.assertFalse(self.motor.Enabled)
    def test_directLinearMovementBack(self):
        mm = hal.Movement(self.motor,-15)
        for i in range(15):
            mm.Step()
            if mm.Done():
                break
        self.assertLess(self.motor.Position,-15)
        self.assertTrue(mm.Done())
        self.assertFalse(self.motor.Enabled)
    def test_LinearMovement(self):
        self.mc.add(hal.Movement(self.motor,15))
        time.sleep(0.06)
        self.assertGreater(self.motor.Position,15)
        self.assertFalse(self.motor.Enabled)
    def test_LinearMovementBack(self):
        self.mc.add(hal.Movement(self.motor,-30))
        time.sleep(0.06)
        self.assertLess(self.motor.Position,-15)
        #self.assertTrue(mm.Done())
        self.assertFalse(self.motor.Enabled)
class MotorAxisTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('mc',Autostart=False)
        self.motor = TestMotor('mot')
        self.la = hal.LinearAxis('ax',self.motor,self.mc,Max=100)
        self.ra = hal.RotationAxis('rx',self.motor,self.mc)
    def test_AbsouluteMovement(self):
        self.la.Move(9)
        for i in range(7):
            self.mc.step()
        self.assertEqual(self.motor.Position,9)
    def test_LinearMovement(self):
        self.la.Move()
        for i in range(5):
            self.mc.step()
        self.assertEqual(self.motor.Position,9)
    def test_LinearMovementBack(self):
        self.la.Move(Speed=-self.motor.maxRPM)
        for i in range(5):
            self.mc.step()
        self.assertEqual(self.motor.Position,-9)
    def test_RotaryMovementP(self):
        self.ra.Move()
        for i in range(5):
            self.mc.step()
        self.assertEqual(self.motor.Position,9)
    def test_RotaryMovementN(self):
        self.ra.Move(Speed=-self.motor.maxRPM)
        for i in range(5):
            self.mc.step()
        #apos = self.ra.Position
        #self.assertEqual(apos,360-9)
if __name__ == '__main__':
    unittest.main()