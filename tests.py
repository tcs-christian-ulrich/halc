import unittest,hal,time
class TestMotor(hal.StepperMotor):
    def __init__(self, id, parent=None):
        hal.StepperMotor.__init__(self, id, parent=None)
        self.Position = 0
    def Step(self,Steps,Direction):
        if Direction>0:
            self.Position += Steps
        else:
            self.Position -= Steps
class MotorTests(unittest.TestCase):
    def setUp(self):
        self.mc = hal.MotorController('0')
        self.motor = TestMotor('1')
    def test_LinearMovement(self):
        self.mc.add(hal.Movement(self.motor,5))
        time.sleep(0.1)
        self.assertEqual(self.motor.Position,5)
if __name__ == '__main__':
    unittest.main()