from . import hal
import threading,time
try:
    from pyroute2 import IW
    from pyroute2 import IPRoute
    ip = IPRoute()
    #to be able to scan for networks python executable must have cap_net_admin flag
    #sudo setcap cap_net_admin,cap_net_raw+ep /usr/bin/python3.8
    iw = IW()
except:pass
class IPRoute2Interface(hal.NetworkInterface):
    def __init__(self, id, parent=None):
        hal.NetworkInterface.__init__(self,id,parent)
        self.idx = ip.link_lookup(ifname=id)[0]    
    def up(self,Up=True): 
        try:
            if Up:
                ip.link('set', index=self.idx, state='up')
            else:
                ip.link('set', index=self.idx, state='down')
            return True
        except:
            return False
    def down(self):
        return self.up(False)
    def addAddress(self,address,pefixlen=24):
        try:
            ip.addr('add', index=self.idx, address=address, prefixlen=prefixlen)
            return True
        except:
            return False
class IPRoute2WifiInterface(hal.NetworkWifiInterface):
    def Scan(self): pass
    def Connect(self,ssid,passphrase=None): pass
    def Disconnect(self): pass
class Enumerate(threading.Thread): 
    def run(self):
        global ip,iw
        while threading.main_thread().is_alive():
            try:
                for dev in hal.Devices.Modules:
                    if isinstance(dev,IPRoute2Interface)\
                    or isinstance(dev,IPRoute2WifiInterface):
                        dev.Found = False
                for link in ip.get_links():
                    adev = None
                    adev = hal.Devices.find(link.get_attr('IFLA_IFNAME'),hal.NetworkInterface)
                    if adev is None:
                        try:
                            index = ip.link_lookup(ifname=link.get_attr('IFLA_IFNAME'))[0]
                            iw.get_interface_by_ifindex(index)
                            adev = IPRoute2WifiInterface(link.get_attr('IFLA_IFNAME'))
                        except:
                            adev = IPRoute2Interface(link.get_attr('IFLA_IFNAME'))
                for dev in hal.Devices.Modules:
                    if isinstance(dev,IPRoute2Interface)\
                    or isinstance(dev,NetworkWifiInterface):
                        if dev.Found == False:
                            del(dev)
            except: pass
            time.sleep(3)
enumerate = Enumerate() 
enumerate.start()        