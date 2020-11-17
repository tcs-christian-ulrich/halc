import os,sys,unittest,time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from halc import hal,remote
import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
from rpyc import SlaveService
class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadedServer(SlaveService, port=18878, auto_register=False)
        self.server.logger.quiet = False
        self.server._start_in_thread()
    def tearDown(self):
        while self.server.clients:
            pass
        self.server.close()
    def testConnection(self):
        conn = rpyc.classic.connect("localhost", port=18878)
        print(conn.modules.sys)
        print(conn.modules["xml.dom.minidom"].parseString("<a/>"))
        conn.execute("x = 5")
        self.assertEqual(conn.namespace["x"], 5)
        self.assertEqual(conn.eval("1+x"), 6)
        conn.close()
    def testHalConnect(self):
        conn = remote.RPyCModules('localhost')
        conn.Connect()
        conn.Disconnect()
if __name__ == '__main__':
    unittest.main()        