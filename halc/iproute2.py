from . import hal
import threading
try:
    from pyroute2 import IW
    from pyroute2 import IPRoute
    ip = IPRoute()
    #to be able to scan for networks python executable must have cap_net_admin flag
    #sudo setcap cap_net_admin,cap_net_raw+ep /usr/bin/python3.8
    iw = IW()
except:pass
class IPRoute2Interface(hal.NetworkInterface):pass
class IPRoute2WifiInterface(hal.NetworkWifiInterface):pass
class Enumerate(threading.Thread): 
    def run(self):
        print('start enumeration')
        global ip,iw
        while threading.main_thread().isAlive():
            try:
                for dev in hal.Devices.Modules:
                    if isinstance(dev,IPRoute2Interface)\
                    or isinstance(dev,IPRoute2WifiInterface):
                        dev.Found = False
                for link in ip.get_links():
                    adev = None
                    if link.get_attr('IFLA_IFNAME')!='lo':
                        adev = hal.Devices.find(link.get_attr('IFLA_IFNAME'),hal.NetworkInterface)
                        if adev is None:
                            try:
                                index = ip.link_lookup(ifname=link.get_attr('IFLA_IFNAME'))[0]
                                iw.get_interface_by_ifindex(index)
                                adev = IPRoute2WifiInterface(link.get_attr('IFLA_IFNAME'))
                            except:
                                adev = IPRoute2Interface(link.get_attr('IFLA_IFNAME'))
                            print(adev)
                for dev in hal.Devices.Modules:
                    if isinstance(dev,IPRoute2Interface)\
                    or isinstance(dev,NetworkWifiInterface):
                        if dev.Found == False:
                            del(dev)
            except: pass
enumerate = Enumerate() 
enumerate.start()        