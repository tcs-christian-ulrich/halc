from . import hal
try:from pyroute2 import IW
except:pass
class IPRoute2Interface(hal.IPInterface):pass
class IPRoute2WifiInterface(hal.IPWifiInterface):pass