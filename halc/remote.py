from . import hal
try: import rpyc
except: print('RPyC is not installed')
class RPyCModules(hal.Proxy):
    def Connect(self,Host=None,Port=18878):
        if Host is None:
            self.conn = rpyc.classic.connect(self._id, port=Port)
        else:
            self.conn = rpyc.classic.connect(Host, port=Port)
    def Disconnect(self):
        self.conn.close()
