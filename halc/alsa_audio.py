import threading,subprocess,time
from . import hal
try: 
    import alsaaudio 
    class  ALSAAudio(hal.AnalogAudioIO):
        def __init__(self, id, hw ,parent=None):
            sensors.AudioADC.__init__(self,id,parent)
            self.hw = hw
            self.Found = True
        def SetInputVolume(self,Volume,channel = None):
            if 'Mic' in alsaaudio.mixers(device=self.hw):
                mixer = alsaaudio.Mixer('Mic',device=self.hw)
            else:
                return False
            vols = mixer.getvolume(alsaaudio.PCM_CAPTURE)
            if channel is None:
                for i in range(len(vols)):
                    mixer.setvolume(Volume,i,alsaaudio.PCM_CAPTURE)
            else:
                mixer.setvolume(Volume,channel,alsaaudio.PCM_CAPTURE)
            return True
        def SampleToWav(self,Filename,Time,SampleFormat='cd',Blocking=False):
            recparams = ['/usr/bin/arecord','-D','plug'+self.hw,'-f',SampleFormat,'-d','1','-r','44100','/tmp/actsweep.wav']
            r=subprocess.Popen(recparams, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self._sampleproc = r
            if Blocking==True:
                return self.StopSampling()
            else:
                return True
        def StopSampling(self):
            r = self._sampleproc
            r.wait()
            res = r.stderr.read().decode().split('\n')
            res += r.stdout.read().decode().split('\n')
            if 'error' in res:
                return False
            return True
        def SetOutputVolume(self,Volume,channel = None):
            if 'PCM' in alsaaudio.mixers(device=self.hw):
                mixer = alsaaudio.Mixer('PCM',device=self.hw)
            elif 'Speaker' in alsaaudio.mixers(device=self.hw):
                mixer = alsaaudio.Mixer('Speaker',device=self.hw)
            else:
                return False
            vols = mixer.getvolume(alsaaudio.PCM_PLAYBACK)
            if channel is None:
                for i in range(len(vols)):
                    mixer.setvolume(Volume,i)
            else:
                mixer.setvolume(Volume,channel)
            return True
        def OutputFromWav(self,Filename):
            playparams = ['/usr/bin/aplay','-D','plug'+self.hw,Filename]
            ap=subprocess.Popen(playparams, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ap.wait()
            res = ap.stdout.read().decode().split('\n')
            if 'error' in res:
                return False
            return True
    class ALSAEnumerate(threading.Thread): 
        def __init__(self): 
            threading.Thread.__init__(self) 
        def run(self):
            while threading.main_thread().isAlive():
                for dev in hal.Devices.Modules:
                    if isinstance(dev,ALSAAudio):
                        dev.Found = False
                try:
                    for i in alsaaudio.card_indexes():
                        (name, longname) = alsaaudio.card_name(i)
                        if hal.Devices.find(name) == None:
                            ALSAAudio(name,"hw:"+str(i))
                        else:
                            hal.Devices.find(name,ALSAAudio).Found = True
                except: pass
                for dev in hal.Devices.Modules:
                    if isinstance(dev,ALSAAudio):
                        if dev.Found == False:
                            #print("deleting "+dev._id)
                            del(dev)
                time.sleep(0.3)
            return
    enumerate = ALSAEnumerate() 
    enumerate.start()
except: print("pyalsaaudio not installed !")