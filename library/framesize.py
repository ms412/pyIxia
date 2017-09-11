
import time
from library.ixiaIf import TclClient
from tools.logger import Logger

class Framesize(object):

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

    def stat(self):
        for _port in self._portlist:
            self._api.call('stat setDefault')
            if self._api.call_rc('stat set %d %d %d' % (_port[0], _port[1], _port[2])) != 0:
                exit()
          #  self._api.call('stat write %d %d %d' % (_port[0], _port[1], _port[2]))

    def felxibleTimestamp(self):
        for _port in self._portlist:
            self._api.call('flexibleTimestamp setDefault')
            self._api.call('flexibleTimestamp set %d %d %d' % (_port[0], _port[1], _port[2]))

    def filter(self):
        for _port in self._portlist:
            self._api.call('filter setDefault')
            self._api.call('filter config -captureTriggerFrameSizeFrom 12')
            self._api.call('filter config -captureTriggerFrameSizeTo 12')
            self._api.call('filter config -captureFilterFrameSizeFrom 12')
            self._api.call('filter config -captureFilterFrameSizeTo 12')
            self._api.call('filter setDefault')
            self._api.call('filter set %d %d %d' % (_port[0], _port[1], _port[2]))

    def filterPallette(self):
        for _port in self._portlist:
            self._api.call('filterPallette setDefault')
            self._api.call('filterPallette set %d %d %d' % (_port[0], _port[1], _port[2]))

    def capture(self):
        for _port in self._portlist:
            self._api.call('capture setDefault')
            self._api.call('capture set %d %d %d' % (_port[0], _port[1], _port[2]))

    def interfaceTable(self):
      #  for _port in self._portlist:
        self._api.call('interfaceTable setDefault')
        self._api.call('interfaceTable write')
        self._api.call('interfaceTable write')

        self._api.call('interfaceTable clearAllInterfaces')
        self._api.call('interfaceTable write')

    def protocolServer(self):
        for _port in self._portlist:
            self._api.call('protocolServer setDefault')
            self._api.call('protocolServer set %d %d %d' % (_port[0], _port[1], _port[2]))

    def stream(self,framesize):
        self._api.call('stream setDefault')
        self._api.call('stream config -name %s'% 'TestStream')
        self._api.call('stream config -framesize %d'% int(framesize))
        self._api.call('stream config -ifg 96.0')
       # self._api.call('stream config -ifgMIN 952.0')
        #self._api.call('stream config -ifgMAX 1016.0')
       # self._api.call('stream config -ibg 96.0')
        self._api.call('stream config -percentPacketRate 100.0')
        self._api.call('stream config -enableTimestamp true')
        self._api.call('stream config -patternType patternTypeRandom')
        self._api.call('stream config -dataPattern allOnes')
        self._api.call('stream config -pattern "FF FF"')
        self._api.call('stream config -frameType "FF FF"')
        self._api.call('stream config -dma stopStream')
        self._api.call('stream config -numFrames 1000')
        #required for lartency
    #    self._api.call('stream config -fir true')

        for _port in self._portlist:
            self._api.call('stream set %d %d %d %d'%(_port[0], _port[1], _port[2],1))

    def pauseFrame(self):
        self._api.call('stream setDefault')
      #  self._api.call('stream config -name %s'% 'PauseStream')

        self._api.call('protocol setDefault')
        self._api.call('protocol config -name PauseStream')
        self._api.call('protocol config -ethernetType ethernetII')

        self._api.call('pauseControl setDefault')
        self._api.call('pauseControl config -da {01 80 C2 00 00 01}')
        self._api.call('pauseControl config -pauseTime 128')

        for _port in self._portlist:
            self._api.call('pauseControl set %d %d %d'%(_port[0], _port[1], _port[2]))

        for _port in self._portlist:
            self._api.call('stream set %d %d %d %d'%(_port[0], _port[1], _port[2],1))

    def protocol(self):
        self._api.call('protocol setDefault')

    def packetGroup(self):
        self._api.call('packetGroup setDefault')
        self._api.call('packetGroup config -groupId 1')
        self._api.call('packetGroup config -groupOffset 16')
        self._api.call('packetGroup config -sequenceNumberOffset 28')
        self._api.call('packetGroup config -insertSequenceSignature true')

        for _port in self._portlist:
            self._api.call('packetGroup setTx %d %d %d %d'%(_port[0], _port[1], _port[2],1))

    def dataInegrity(self):
        self._api.call('dataInegrity setDefault')
        self._api.call('dataIntegrity config -signatureOffset 12')
        self._api.call('dataIntegrity config -signature "08 71 18 00"')

    def result(self):
        _result = {}
        for _port in self._portlist:
            _str_port = (str(_port[0])+str(_port[1])+str(_port[2]))
            print(_str_port)
            _result[_str_port] = {}

        for _port in self._portlist:
            self._api.call_rc('capture get %d %d %d' % (_port[0],_port[1], _port[2]))
            self._api.call('capture cget -nPackets')
        for _port in self._portlist:
            self._api.call_rc('captureBuffer get %d %d %d' % (_port[0],_port[1],_port[2]))
            self._api.call_rc('captureBuffer getStatistics')
            print('Port %s Latency: %d' % (str(_port), int(self._api.call('captureBuffer cget -averageLatency')[0])))

        for _port in self._portlist:
            self._api.call('stat get statAllStats %d %d %d'% (_port[0], _port[1], _port[2]))
          #  print('Port %s LinkState: %d'% (str(_port), int(self._api.call('stat cget -link')[0])))
          #  print('Port %s txFrames: %d'% (str(_port), int(self._api.call('stat cget -framesSent')[0])))
          #  print('Port %s rxFrames: %d'% (str(_port), int(self._api.call('stat cget -framesReceived')[0])))
          #  print('Port %s txBytes: %d'% (str(_port), int(self._api.call('stat cget -bytesSent')[0])))
          #  print('Port %s rxBytes: %d'% (str(_port), int(self._api.call('stat cget -bytesReceived')[0])))
          #  print('Port %s Line Rate: %d'% (str(_port), int(self._api.call('stat cget -lineSpeed')[0])))
          #  _str_port = (str(_port[0]) + '-' + str(_port[1]) + '-' + str(_port[2]))
            _testResult = {}
            _testResult['txFrame'] = int(self._api.call('stat cget -framesSent')[0])
            _testResult['rxFrame'] = int(self._api.call('stat cget -framesReceived')[0])
            _testResult['txBytes'] = int(self._api.call('stat cget -bytesSent')[0])
            _testResult['rxBytes'] = int(self._api.call('stat cget -bytesReceived')[0])

            _str_port = (str(_port[0]) + str(_port[1]) + str(_port[2]))

            _result[_str_port] = _testResult
        #    _testResult['PORT'] = _port
          #  _resultList.append(_testResult)
      #  print('RESULT',_result)

        return _result


    def framesizeTest(self,sizelist):

        _framesizeTest = {}
        self._api.call('set portList %s' % (self._tclportlist))
        self.createGroup()

        self.port('1Gbe-opt')

        #self.pauseFrame()
         # _result = {}
        for framesize in sizelist:
            self.stat()
            self.felxibleTimestamp()
            self.filter()
            self.capture()
            self.filterPallette()
            self.interfaceTable()
            self.protocolServer()
            self.stream(framesize)

            if self._api.call_rc('ixWriteConfigToHardware portList') != 0:
                exit()

            time.sleep(10)
            if self._api.call_rc('ixCheckLinkState portList') != 0:
                exit()

            if self._api.call_rc('ixStartCapture portList') != 0:
                exit()

            if self._api.call_rc('ixStartTransmit portList') != 0:
                exit()

            time.sleep(10)

            if self._api.call_rc('ixStopCapture portList') != 0:
                exit()

            if self._api.call_rc('ixStopTransmit portList') != 0:
                exit()

          #  _resultList = self.result()

            _framesizeTest[framesize] = self.result()

           # for item in _resultList:
            #    print(item)
             #   _port = item.get('PORT')
             #   _str_port = (str(_port[0]) + '-' + str(_port[1]) + '-' + str(_port[2]))
             #   print(_str_port)
             #   _framesizeTest[_str_port]['FRAMESIZE'][framesize] = _str_port

              #  print(_framesizeTest)

         #   _testresult = self.result()
          #  print('TESTRESULT', _testresult)

        return _framesizeTest


    def disconnect(self):
        if self._api.call_rc('ixClearOwnership %s' % (self._tclportlist)) != 0:
            exit()


