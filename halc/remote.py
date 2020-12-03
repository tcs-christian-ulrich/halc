from . import hal
try: import rpyc
except: print('RPyC is not installed')
import threading,time
class RPyCModules(hal.Proxy):
    def Connect(self,Host=None,Port=18878):
        if Host is None:
            self.conn = rpyc.classic.connect(self._id, port=Port)
        else:
            self.conn = rpyc.classic.connect(Host, port=Port)
    def Disconnect(self):
        self.conn.close()
    def LoadModule(self,Name):
        return self.conn.modules[Name]
class Enumerate(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
    def run(self):
        try:
            from rpyc.utils import registry
            registrar = registry.UDPRegistryClient()
            while threading.main_thread().isAlive():
                try:
                    for dev in hal.Devices.Modules:
                        if isinstance(dev,RPyCModules):
                            dev.Found = False
                    services = registrar.discover('slave')
                    for service in services:
                        ip,port = service
                        adev = hal.Devices.find(ip,RPyCModules)
                        if adev == None:
                            print(ip,port)
                        else:
                            adev.Found = True
                    for dev in hal.Devices.Modules:
                        if isinstance(dev,RPyCModules):
                            if dev.Found == False:
                                del(dev)
                    time.sleep(1)
                except: 
                    pass
        except: pass
enumerate = Enumerate() 
enumerate.start()