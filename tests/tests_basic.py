import os,sys,unittest,time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from halc import hal
class BasicTests(unittest.TestCase):
    def setUp(self):
        self.sensor1 = hal.Sensor('Pon')
        self.sensor1.Name = 'Pon'
        self.sensor2 = hal.Sensor('P')
        self.sensor2.Name = 'P'
        self.sensor3 = hal.Sensor('Aoff')
        self.sensor3.Name = 'Aisoff'
    def tearDown(self) -> None:
        self.sensor1.destroy()
        self.sensor2.destroy()
        return super().tearDown()
    def testFindSharp(self):
        self.assertEqual(hal.Devices.find('P'),self.sensor2)
        self.assertEqual(hal.Devices.find('Pon'),self.sensor1)
    def testFindUnsharp(self):
        self.assertEqual(hal.Devices.find('P',None,None,True),self.sensor1)
    def testFindSharpName(self):
        self.assertEqual(hal.Devices.find(None,None,'P'),self.sensor2)
        self.assertEqual(hal.Devices.find(None,None,'Pon'),self.sensor1)
    def testFindUnsharpName(self):
        self.assertEqual(hal.Devices.find(None,None,'P',True),self.sensor1)
    def testEnsureDeviceName(self):
        self.assertTrue(hal.EnsureDevice(hal.Sensor,'Aisoff',0.1))
    def testEnsureDeviceID(self):
        self.assertTrue(hal.EnsureDevice(hal.Sensor,'Aoff',0.1))
if __name__ == '__main__':
    unittest.main()