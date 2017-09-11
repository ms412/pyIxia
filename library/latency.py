
import time
from library.ixiaIf import TclClient
from tools.logger import Logger

class Latencyframe(object):

    def __init__(self, *args):
        self._api = TclClient()
        self._log = Logger()
        self._portlist=[]
        self._tclportlist =''

        for item in args:
            self._portlist.append([self._api.chassisID(),item[0],item[1]])

        for item in self._portlist:
            self._tclportlist = (self._tclportlist + '[list %d %d %d] ' % (item[0], item[1], item[2]))

        self._tclportlist=('[list %s]'%(self._tclportlist))

    def __del__(self):
        self.disconnect()

    def createGroup(self):
        self._api.call('set group 12')
        self._api.call('portGroup create $group')
        for _port in self._portlist:
            self._api.call('portGroup add $group %d %d %d' % (_port[0], _port[1], _port[2]))
           # self._api.call('port setFactoryDefaults %d %d %d' % (_port[0], _port[1], _port[2]))
        self._api.call('portGroup write $group')
        self._api.call('portGroup setCommand $group resetStatistics')
       # self._api.call('portGroup write $group')
        time.sleep(2)

    def port(self,mode):
        print('port config',self._portlist)
    #    self._api.call('set portlist %s'%(self._TclPortList()))
      #  if self._api.call_rc('ixTakeOwnership portlist force') != 0:
        if self._api.call_rc('ixTakeOwnership %s force'%(self._tclportlist)) != 0:
            print('EXIT')
            exit()
        for _port in self._portlist:
            if '1Gbe-opt' in mode:

                print('config prot',_port)
                self._api.call('port setDefault')
                #optisch
                self._api.call('port setPhyMode 1 %d %d %d'% (_port[0], _port[1], _port[2]))
                self._api.call('port config -speed 1000')
                self._api.call('port config -advertise100FullDuplex false')
                self._api.call('port config -advertise100HalfDuplex false')
                self._api.call('port config -advertise10FullDuplex false')
                self._api.call('port config -advertise10HalfDuplex false')
                self._api.call('port config -advertise1000FullDuplex true')
                self._api.call('port config -speed 1000')
                self._api.call('port set %d %d %d' % (_port[0], _port[1], _port[2]))

            elif '1Gbe-el'in mode:
                self._api.call('port setDefault')
                # electrical
                self._api.call('port setPhyMode 0 %d %d %d' % (_port[0], _port[1], _port[2]))
                self._api.call('port config -speed 1000')
                self._api.call('port config -advertise100FullDuplex false')
                self._api.call('port config -advertise100HalfDuplex false')
                self._api.call('port config -advertise10FullDuplex false')
                self._api.call('port config -advertise10HalfDuplex false')
                self._api.call('port config -advertise1000FullDuplex true')
                self._api.call('port config -speed 1000')
                self._api.call('port set %d %d %d' % (_port[0], _port[1], _port[2]))
            else:
                print('nothing')


    def configure(self):
        self._api.call('set streamID 1')
        self._api.call('stream setDefault')
        self._api.call('stream config -name %s' %'LatencyTest')
        self._api.call('stream config -numFrames 4')
        self._api.call('stream config -numBursts 240')
        self._api.call('stream config -sa {00 00 00 01 01 01}')
        self._api.call('stream config -sa {00 00 00 01 01 02}')
        self._api.call('stream config -fir true')
        self._api.call('stream config -dma stopStream')
        self._api.call('stream config -frameSizeType sizeIncr')
        self._api.call('stream config -frameSizeMIN 64')
        self._api.call('stream config -frameSizeMAX 1024')
        self._api.call('stream config -frameSizeStep 64')
        self._api.call('stream config -enableIbg false')
        self._api.call('stream config -enableIsg false')
        self._api.call('stream config -rateMode usePercentRate')
        self._api.call('stream config -percentPacketRate 50')

        self._api.call('udf setDefault')
        self._api.call('udf config -enable true')
        self._api.call('udf config -counterMode udfCounterMode')
        self._api.call('udf config -continuousCount false')
        self._api.call('udf config -initval 0')
        self._api.call('udf config -repeat 4')
        self._api.call('udf config -udfSize c16')
        self._api.call('udf config -offset 52')
       # print('udf set return',self._api.call('udf set 1'))
       # print('udf set return', self._api.call_r('udf set 1'))
        self._api.call('udf set 1')
     #   if self._api.call_r('udf set 1') != 0:
      #      print('failed')
       #     exit()

        _portTx = self._portlist[0]
        self._api.call('stream set %d %d %d %d'%(_portTx[0], _portTx[1], _portTx[2],1))

        self._api.call('packetGroup setDefault')
        self._api.call('packetGroup config -insertSignature true')
        self._api.call('packetGroup setTx %d %d %d 1' % (_portTx[0], _portTx[1], _portTx[2]))


    #Receiver
        _portRx = self._portlist[1]
        self._api.call('port config -receiveMode $::portRxModeWidePacketGroup')
        self._api.call('port set %d %d %d' % (_portRx[0], _portRx[1], _portRx[2]))

        self._api.call('packetGroup setDefault')
        self._api.call('packetGroup config -latencyControl storeAndForward')
        self._api.call('packetGroup config -enableLatencyBins true')
        self._api.call('packetGroup config -latencyBinList {0.70 0.72 0.74 0.76}')
        self._api.call('packetGroup setRx %d %d %d' % (_portRx[0], _portRx[1], _portRx[2]))

    def latencyTest(self):
        self._api.call('set portList %s' % (self._tclportlist))
        self.configure()
       # time.sleep(10)
        _portRx = self._portlist[1]
        _portTx = self._portlist[0]

        if self._api.call_rc('ixWriteConfigToHardware portList') != 0:
            exit()
        time.sleep(10)
        if self._api.call_rc('ixCheckLinkState test') != 0:
            exit()

        self._api.call('ixStartPortPacketGroups %d %d %d'%  (_portRx[0], _portRx[1], _portRx[2]))
        self._api.call('ixStartPortTransmit %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

        time.sleep(10)

        self._api.call('ixCheckPortTransmitDone %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

        self._api.call('ixStopPortPacketGroups %d %d %d' % (_portRx[0], _portRx[1], _portRx[2]))

        if self._api.call_rc('packetGroupStats get %d %d %d 0 16384' % (_portRx[0], _portRx[1], _portRx[2])) != 0:
            exit()

        return self.result()




    def result(self):
        _testResult = {}
        self._api.call('set numGroups [packetGroupStats cget -numGroups]')
        print('numGroups',self._api.call('packetGroupStats cget -numGroups'))
        self._api.call('set numRxLatencyBins [packetGroupStats cget -numLatencyBins]')
        print('numRxLatency', self._api.call('packetGroupStats cget -numLatencyBins'))
        self._api.call('set totalFrames [packetGroupStats cget -totalFrames]')
        print('latenchy',self._api.call('set totalFrames [packetGroupStats cget -totalFrames]'))
        self._api.call('set totalFrames [packetGroupStats cget -totalFrames]')
        _totalFrames = self._api.call('packetGroupStats cget -totalFrames')
        print('totalFrame',_totalFrames)
        for x in range (0,4):
            print(x,self._api.call('packetGroupStats getGroup %d'%x))
            print('total Frames',self._api.call('packetGroupStats cget -totalFrames'))




        _testResult['TotalFrames']= self._api.call_r('packetGroupStats cget -totalFrames')
        _testResult['minLatency']= self._api.call_r('packetGroupStats cget -minLatency')
        _testResult['maxLatency']= self._api.call_r('packetGroupStats cget -maxLatency')
        _testResult['averageLatency'] = self._api.call_r('packetGroupStats cget -averageLatency')
        _testResult['byteRate'] = self._api.call_r('packetGroupStats cget -byteRate')
        _testResult['frameRate'] = self._api.call_r('packetGroupStats cget -frameRate')
        _testResult['standaredDeviation'] = self._api.call_r('packetGroupStats cget -standardDeviation')

        print('TestResult',_testResult)

        return _testResult



    def disconnect(self):
        if self._api.call_rc('ixClearOwnership %s' % (self._tclportlist)) != 0:
            exit()


