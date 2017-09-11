
import socket
from tools.logger import Logger


class TclError(Exception):
    def __init__(self, result):
        self.result = result
    def __repr__(self):
        return '%s(result="%s")' % (self.__class__.__name__, self.result)
    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.result)


class TclClient:
    instance = None
    def __init__(self,log = None):
        if not TclClient.instance:
            TclClient.instance = TclClient.__TclClient(log)
        else:
            TclClient.instance.val = log

    def __getattr__(self, item):
        return getattr(self.instance, item)

    class __TclClient:
        def __init__(self, log=None):
            self._host = '192.168.115.80'
            self._port = 4555
            self._log = Logger()
            self._user = 'IXIA'
            self._fd = None
            self._chassisID = 0
            self._buffersize = 10240

        def __del__(self):
            self.close()

        def _call(self, string, *args):

            if self._fd is None:
                raise RuntimeError('TclClient is not connected')

            string += '\r\n'
            data = string % args
            self._log.debug('Send data %s'% (str(data)))
            self._fd.send(data.encode('ascii'))

            data = self._fd.recv(self._buffersize).decode('utf8')
            self._log.debug('data=(%s)'%(data))

            assert data[-2:] == '\r\n'
            tcl_result = int(data[-3])

            data = data[:-3].rsplit('\r', 1)
            if len(data) == 2:
                io_output, result = data
            else:
                result = data[0]
                io_output = None

            if tcl_result == 1:
                assert io_output == None
                raise TclError(result)

            return result, io_output

        def call(self, cmd, *args):
            print('api_call',cmd,*args)
            return self._call(cmd, *args)

        def call_r(self, cmd, *args):
            return self._call(cmd, *args)[0]

        def call_rc(self, cmd, *args):
            print('call_rc',cmd, *args)
        #    rc = self.call(cmd, *args)[0]
            rc = self._call(cmd, *args)[0]
            #print('responce',rc)
          #  rc =rc[0]
            if int(rc) != 0:
                print('error responce')
                raise TclError(rc)
            else:
                print('Return',rc)
                return int(rc)

        def connect(self,host,port,user):
            self._host = host
            self._port = port
            self._user = user

            self._log.info('Connect to %s, %s' % (self._host,self._port))

            self._fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._fd.connect((self._host, self._port))

            self.call('package req IxTclHal')
            self._log.info(self.call_r('version cget -ixTclHALVersion'))

        def session(self):
            _result = False
            if self.call_rc('ixConnectToChassis %s' % self._host) != 0:
                self._log.error('Failed to Connect to Chassis %s'% (str(self._host)))
                _result = False
            else:
                self._log.info('Success Connected to Chassis %s'% (str(self._host)))
                _result = True

            self._chassisID = int(self.call_r('ixGetChassisID %s'% self._host))
            self._log.info('Chassis ID %d' % self._chassisID)
          #  print('chass', _chassisID)

            if self.call_rc('ixLogin %s' % self._user) != 0:
                self._log.debug('Failed User Login %s '% (self._user))
                _result = False
            else:
                self._log.info('Success User Login %s ' % (self._user))
                _result = True

            return _result

        def chassisID(self):
      #      print('chassisid',self._chassisID)
            return self._chassisID

        def close(self):
            self._log.info('Disconnect from Chassis %s' % (str(self._host)))
            print('Closing connection')
         #   self._log.debug(_msg)
            self._fd.close()
            self._fd = None


class logger(object):

    def info(self,msg):
        print(msg)

    def debug(self,msg):
        print(msg)

if __name__ == "__main__":
    log = logger()
    y = TclClient(log)
    y.connect('172.17.115.80', 4555, 'IXIA')
    z = TclClient()
    z.session()