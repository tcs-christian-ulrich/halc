from . import hal
import threading,time,subprocess
try: from zeroconf import ServiceBrowser, Zeroconf
except: print('zeroconf is not installed')
class Enumerate:
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
zeroconf = Zeroconf()
enumerate = Enumerate()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)