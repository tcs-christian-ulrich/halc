from . import hal
try: import rpyc
except: print('RPyC is not installed')
import threading,time,logging
class RPyCModules(hal.Proxy):
    def __init__(self, id, parent=None):
        self.Connect(id)
        hal.Proxy.__init__(self,id,parent)
        self.hal = None
    def find(self,id=None,typ=None,Name=None):
        rsys = self.conn.modules.sys
        if self.hal is None:
            for module in rsys.modules:
                if 'halc.hal' in str(module):
                    self.hal = self.conn.modules[module]
        if self.hal is not None:
            return self.hal.Devices.find(id,typ,Name)
        return None
    @property
    def Modules(self):
        if self.hal is not None:
            return self.hal.Devices.Modules
        else:
            return []
    def Connect(self,Host=None,Port=18812):
        if Host is None:
            self.conn = rpyc.classic.connect(self._id, port=Port)
        else:
            self.conn = rpyc.classic.connect(Host, port=Port)
    def Disconnect(self):
        self.conn.close()
    def AddPath(self,Path):
        try:
            rsys = self.conn.modules.sys
            rsys.path.insert(0,Path)
            return True
        except:
            return False
    def LoadModule(self,Name):
        try:
            return self.conn.modules[Name]
        except BaseException as e:
            self.logger.debug(str(e))
            return False
class Enumerate(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
    def run(self):
        try:
            from rpyc.utils import registry
            registrar = registry.UDPRegistryClient()
            while threading.main_thread().is_alive():
                try:
                    for dev in hal.Devices.Modules:
                        if isinstance(dev,RPyCModules):
                            dev.Found = False
                    services = registrar.discover('slave')
                    for service in services:
                        ip,port = service
                        adev = hal.Devices.find(ip,RPyCModules)
                        if adev == None:
                            try:
                                dev = RPyCModules(ip)
                                #print(ip,port)
                            except BaseException as e: 
                                logging.debug(str(e))
                                del(dev)
                        else:
                            adev.Found = True
                    for dev in hal.Devices.Modules:
                        if isinstance(dev,RPyCModules):
                            if dev.Found == False:
                                del(dev)
                except BaseException as e: 
                    logging.debug(str(e))
                time.sleep(1)
        except BaseException as e:
            logging.debug(str(e))
enumerate = Enumerate() 
enumerate.start()