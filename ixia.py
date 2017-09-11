
import time
from tools.logger import Logger
from library.ixiaIf import TclClient
from library.latency_new import Latencyframe
from library.framesize import Framesize
from library.pauseframe import Pauseframe



class manager(object):

    def __init__(self):
        self._log = None
        self._testResults = {}

    def logging(self):
        self._log = Logger('IXIA')
        self._log.handle()
        self._log.info('TEST')

    def connect(self):
        _ix = TclClient()
        _ix.connect('172.17.115.80', 4555, 'IXIA')
        _ix.session()

    def runTest(self):
     #   _frame = Framesize([4,2],[4,3])
      #  _frame.port('1Gbe-opt')
      #  self._testResults['FRAMESIZE']=_frame.framesizeTest([64,256,512,768,1024,1218,1518,9600])
      #  _frame.disconnect()

     #   _pause=Pauseframe([4,2],[4,3])
     #   self._testResults['PAUSEFRAME']=_pause.pauseframeTest()
     #   _pause.disconnect()

        _latency=Latencyframe([4,2],[4,3])
        _latency.port('1Gbe-opt')
        self._testResults['LATENCYFRAME']=_latency.latencyTest()
        _latency.disconnect()

        print(self._testResults)



if __name__ == '__main__':
    mgr = manager()
    mgr.logging()
    mgr.connect()
    mgr.runTest()
