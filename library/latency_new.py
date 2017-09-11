
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

        self._txPortList = self._portlist[0]
        self._rxPortList = self._portlist[1]

        self._tcl_txPortList = (('[list [list %d %d %d]]')% (self._txPortList[0],self._txPortList[1],self._txPortList[2]))
        self._tcl_rxPortList = (('[list [list %d %d %d]]') % (self._rxPortList[0], self._rxPortList[1], self._rxPortList[2]))

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
        _portTx = self._portlist[0]

        self._api.call('set streamID 1')
        self._api.call('stream setDefault')
        self._api.call('stream config -enable true')
        self._api.call('stream config -name %s' %'LatencyTest')
        self._api.call('stream config -dma stopStream')
        self._api.call('stream config -numFrames 100')
        self._api.call('stream config -numBursts 1')
        self._api.call('stream config -rateMode usePercentRate')
        self._api.call('stream config -percentPacketRate 100')
        self._api.call('stream config -sa {00 00 00 01 01 01}')
        self._api.call('stream config -sa {00 00 00 01 01 02}')
        self._api.call('stream config -fir true')
        self._api.call('stream config -framesize %d'% int(100))

        self._api.call('ip setDefault')
        self._api.call('ip set %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

        self._api.call('tcp setDefault')
        self._api.call('tcp set %d %d %d'%(_portTx[0], _portTx[1], _portTx[2]))

        self._api.call('protocol setDefault')
        self._api.call('protocol config -name ipV4')
        self._api.call('protocol config -ethernetType ethernetII')


        self._api.call('stream set %d %d %d %d'%(_portTx[0], _portTx[1], _portTx[2],1))


    #Receiver
        _portRx = self._portlist[1]
        self._api.call('port config -transmitMode portTxPacketFlows')
        self._api.call('port config -receiveMode portRxTcpRoundTrip')
        self._api.call('port set %d %d %d' % (_portRx[0], _portRx[1], _portRx[2]))

        self._api.call('tcpRoundTripFlow setDefault')
        self._api.call('tcpRoundTripFlow config -macSA {00 00 00 01 01 02}')
        self._api.call('tcpRoundTripFlow config -macDA {00 00 00 01 01 01}')
        self._api.call('tcpRoundTripFlow set %d %d %d'% (_portRx[0], _portRx[1], _portRx[2]))


    def latencyTest(self):
        self._api.call('set portList %s' % (self._tclportlist))
        self.configure()
       # time.sleep(10)
        _portRx = self._portlist[1]
        _portTx = self._portlist[0]

        if self._api.call_rc('ixWriteConfigToHardware portList') != 0:
            exit()
        time.sleep(10)
        if self._api.call_rc('ixCheckLinkState portList') != 0:
            exit()

        self._api.call(('ixClearStats %s')%(self._tcl_txPortList))
        self._api.call(('ixStartCapture %s')% (self._tcl_txPortList))
        self._api.call(('ixStartTransmit %s') % (self._tcl_txPortList))


    #    self._api.call('ixStartPortPacketGroups %d %d %d'%  (_portRx[0], _portRx[1], _portRx[2]))
     #   self._api.call('ixStartPortTransmit %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

        time.sleep(10)

        self._api.call('ixCheckPortTransmitDone %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

      #  self._api.call('ixStopPortPacketGroups %d %d %d' % (_portRx[0], _portRx[1], _portRx[2]))

       # if self._api.call_rc('packetGroupStats get %d %d %d 0 16384' % (_portRx[0], _portRx[1], _portRx[2])) != 0:
        #    exit()

        return self.result()




    def result(self):
        _portTx = self._portlist[0]
        _portRx = self._portlist[1]
        self._api.call('capture get %d %d %d' % (_portTx[0], _portTx[1], _portTx[2]))

        self._api.call('set numRxFrames [capture cget -nPackets]')

        self._api.call('captureBuffer get %d %d %d 1 [expr $numRxFrames -1]' % (_portRx[0], _portRx[1], _portRx[2]))

        self._api.call('captureBuffer getStatistics')
        self._api.call('captureBuffer getConstraint 1')

        print('avr Latency', self._api.call('captureBuffer cget -averageLatency'))
        print('min Latency', self._api.call('captureBuffer cget -minLatency'))
        print('max Latency', self._api.call('captureBuffer cget -maxLatency'))




        return



    def disconnect(self):
        if self._api.call_rc('ixClearOwnership %s' % (self._tclportlist)) != 0:
            exit()


