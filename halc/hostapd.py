import threading,subprocess,time,os,logging
from . import hal
try: 
    from PyAccessPoint import pyaccesspoint
    import netifaces
except: print("PyAccessPoint not installed !")
config = '''
#sets the wifi interface to use, is wlan0 in most cases
interface={1}
#driver to use, nl80211 works in most cases
driver=nl80211
#sets the ssid of the virtual wifi access point
ssid={0}
#sets the mode of wifi, depends upon the devices you will be using. It can be a,b,g,n. Setting to g ensures backward compatiblity.
hw_mode=g
#sets the channel for your wifi
channel=6
#macaddr_acl sets options for mac address filtering. 0 means "accept unless in deny list"
macaddr_acl=0
#setting ignore_broadcast_ssid to 1 will disable the broadcasting of ssid
ignore_broadcast_ssid=0
#Sets authentication algorithm
#1 - only open system authentication
#2 - both open system authentication and shared key authentication
auth_algs=1
'''
config_pw = '''
#####Sets WPA and WPA2 authentication#####
#wpa option sets which wpa implementation to use
#1 - wpa only
#2 - wpa2 only
#3 - both
wpa=3
#sets wpa passphrase required by the clients to authenticate themselves on the network
wpa_passphrase={0}
#sets wpa key management
wpa_key_mgmt=WPA-PSK
#sets encryption used by WPA
wpa_pairwise=TKIP
#sets encryption used by WPA2
rsn_pairwise=CCMP
#################################
#####Sets WEP authentication#####
#WEP is not recommended as it can be easily broken into
#wep_default_key=0
#wep_key0=qwert    #5,13, or 16 characters
#optionally you may also define wep_key2, wep_key3, and wep_key4
#################################
#For No encryption, you don't need to set any options
'''
class AccessPoint(hal.NetworkSwitch,pyaccesspoint.AccessPoint): 
    def __init__(self,SSID='TestNetwork',Password='1234567890',IP='192.168.2.1',interface='wlan0', inet=None, netmask='255.255.255.0',
                 enableNat=True,enableDhcp=True):
        self.wlan = interface
        self.inet = inet
        self.ip = IP
        self.netmask = netmask
        self.ssid = SSID
        self.password = Password
        self.nat = enableNat
        self.dhcp = enableDhcp
        self.root_directory = "/tmp"
        self.hostapd_config_path = os.path.join(self.root_directory, "hostapd.config")
        hal.NetworkSwitch.__init__(self,self.ip)
        self.start()
    def _check_parameters(self):
        interfaces = netifaces.interfaces()
        if self.wlan not in interfaces:
            logging.error("Wlan {} interface was not found".format(self.wlan))
            return False
        if self.inet is not None and self.inet not in interfaces:
            logging.error("Inet {} interface was not found".format(self.inet))
            return False
        if not self._validate_ip(self.ip):
            logging.error("Wrong ip {}".format(self.ip))
            return False
        if self.ssid is None:
            logging.error("SSID must not be None")
            return False
        self.ssid = str(self.ssid)
        if self.password is not None:
            self.password = str(self.password)
        return True
    def _write_hostapd_config(self):
        with open(self.hostapd_config_path, 'w') as hostapd_config_file:
            if self.password is not None:
                hostapd_config_file.write(config.format(self.ssid, self.wlan)+config_pw.format(self.password))
            else:
                hostapd_config_file.write(config.format(self.ssid, self.wlan))
    def _start_router(self):
        self._pre_start()
        s = 'ifconfig ' + self.wlan + ' up ' + self.ip + ' netmask ' + self.netmask
        logging.debug('created interface: mon.' + self.wlan + ' on IP: ' + self.ip)
        r = self._execute_shell(s)
        logging.debug(r)
        logging.debug('wait..')
        self._execute_shell('sleep 2')
        i = self.ip.rindex('.')
        ipparts = self.ip[0:i]
        if self.nat:
            # enable forwarding in sysctl.
            logging.debug('enabling forward in sysctl.')
            r = self._execute_shell('sysctl -w net.ipv4.ip_forward=1')
            logging.debug(r.strip())

        if self.inet is not None and self.nat:
            # enable forwarding in iptables.
            logging.debug('creating NAT using iptables: {} <-> {}'.format(self.wlan, self.inet))
            self._execute_shell('iptables -P FORWARD ACCEPT')

            # add iptables rules to create the NAT.
            self._execute_shell('iptables --table nat --delete-chain')
            self._execute_shell('iptables --table nat -F')
            r = self._execute_shell('iptables --table nat -X')
            if len(r.strip()) > 0:
                logging.debug(r.strip())
            self._execute_shell('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format(self.inet))
            self._execute_shell(
                'iptables -A FORWARD -i {} -o {} -j ACCEPT -m state --state RELATED,ESTABLISHED'
                    .format(self.inet, self.wlan))
            self._execute_shell('iptables -A FORWARD -i {} -o {} -j ACCEPT'.format(self.wlan, self.inet))

        if self.nat:
            # allow traffic to/from wlan
            self._execute_shell('iptables -A OUTPUT --out-interface {} -j ACCEPT'.format(self.wlan))
            self._execute_shell('iptables -A INPUT --in-interface {} -j ACCEPT'.format(self.wlan))

        if self.dhcp:
            # start dnsmasq
            s = 'dnsmasq --dhcp-authoritative --interface={} --dhcp-range={}.20,{}.100,{},4h'\
                .format(self.wlan, ipparts, ipparts, self.netmask)
            logging.debug('running dnsmasq')
            logging.debug(s)
            r = self._execute_shell(s)
            logging.debug(r)

        # ~ f = open(os.getcwd() + '/hostapd.tem','r')
        # ~ lout=[]
        # ~ for line in f.readlines():
        # ~ lout.append(line.replace('<SSID>',SSID).replace('<PASS>',password))
        # ~
        # ~ f.close()
        # ~ f = open(os.getcwd() + '/hostapd.conf','w')
        # ~ f.writelines(lout)
        # ~ f.close()

        # writelog('created: ' + os.getcwd() + '/hostapd.conf')
        # start hostapd
        # s = 'hostapd -B ' + os.path.abspath('run.conf')
        s = 'sudo hostapd -B {}'.format(self.hostapd_config_path)
        logging.debug(s)
        logging.debug('killing hostapd')
        self._execute_shell('sudo killall hostapd')
        logging.debug('running hostapd')
        logging.debug('wait..')
        self._execute_shell('sleep 2')
        r = self._execute_shell(s)
        logging.debug(r)
        logging.debug('hotspot is running.')
        return True
    def _stop_router(self):
        # bring down the interface
        os.system('ifconfig mon.' + self.wlan + ' down')

        # stop hostapd
        logging.debug('stopping hostapd')
        os.system('sudo pkill hostapd')
        if self.dhcp:
            # stop dnsmasq
            logging.debug('stopping dnsmasq')
            os.system('killall dnsmasq')
        if self.nat:
            # disable forwarding in iptables.
            logging.debug('disabling forward rules in iptables.')
            self._execute_shell('iptables -P FORWARD DROP')

        # delete iptables rules that were added for wlan traffic.
        if self.wlan != None and self.nat:
            self._execute_shell('iptables -D OUTPUT --out-interface {} -j ACCEPT'.format(self.wlan))
            self._execute_shell('iptables -D INPUT --in-interface {} -j ACCEPT'.format(self.wlan))
        if self.nat:
            self._execute_shell('iptables --table nat --delete-chain')
            self._execute_shell('iptables --table nat -F')
            self._execute_shell('iptables --table nat -X')
            # disable forwarding in sysctl.
            logging.debug('disabling forward in sysctl.')
            r = self._execute_shell('sysctl -w net.ipv4.ip_forward=0')
            logging.debug(r.strip())
            # self.execute_shell('ifconfig ' + wlan + ' down'  + IP + ' netmask ' + Netmask)
            # self.execute_shell('ip addr flush ' + wlan)
        logging.debug('hotspot has stopped.')
        return True
    def release(self):
        self._stop_router()
    def __del__(self):
        self.release()
        super().__del__(self)
def Cleanup():
    AP = hal.Devices.find(None,AccessPoint)
    if AP:
        AP.release()
        del(AP)
        AP = None
