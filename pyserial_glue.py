import pylibftdi
pylibftdi.USB_VID_LIST.append(0x0000)

# some constants from pyserial

# all Python versions prior 3.x convert ``str([17])`` to '[17]' instead of '\x11'
# so a simple ``bytes(sequence)`` doesn't work for all versions
def to_bytes(seq):
    """convert a sequence to a bytes type"""
    if isinstance(seq, bytes):
        return seq
    elif isinstance(seq, bytearray):
        return bytes(seq)
    elif isinstance(seq, memoryview):
        return seq.tobytes()
    else:
        b = bytearray()
        for item in seq:
            b.append(item)  # this one handles int and str for our emulation and ints for Python 3.x
        return bytes(b)

# create control bytes
XON  = to_bytes([17])
XOFF = to_bytes([19])

CR = to_bytes([13])
LF = to_bytes([10])


PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

PARITY_NAMES = {
    PARITY_NONE:  'None',
    PARITY_EVEN:  'Even',
    PARITY_ODD:   'Odd',
    PARITY_MARK:  'Mark',
    PARITY_SPACE: 'Space',
}


# also borrow some exceptions from pyserial

class SerialException(IOError):
    """Base class for serial port related exceptions."""


class SerialTimeoutException(SerialException):
    """Write timeouts give an exception"""


writeTimeoutError = SerialTimeoutException('Write timeout')
portNotOpenError = SerialException('Attempting to use a port that is not open')


# serial base borrowed from pyserial

class SerialBase(object):
    """Serial port base class. Provides __init__ function and properties to
       get/set port settings."""

    # default values, may be overridden in subclasses that do not support all values
    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
                 3000000, 3500000, 4000000)
    BYTESIZES = (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)
    PARITIES  = (PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE)
    STOPBITS  = (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO)

    def __init__(self,
                 port = None,           # number of device, numbering starts at
                                        # zero. if everything fails, the user
                                        # can specify a device string, note
                                        # that this isn't portable anymore
                                        # port will be opened if one is specified
                 baudrate=9600,         # baud rate
                 bytesize=EIGHTBITS,    # number of data bits
                 parity=PARITY_NONE,    # enable parity checking
                 stopbits=STOPBITS_ONE, # number of stop bits
                 timeout=None,          # set a timeout value, None to wait forever
                 xonxoff=False,         # enable software flow control
                 rtscts=False,          # enable RTS/CTS flow control
                 writeTimeout=None,     # set a timeout for writes
                 dsrdtr=False,          # None: use rtscts setting, dsrdtr override if True or False
                 interCharTimeout=None  # Inter-character timeout, None to disable
                 ):
        """Initialize comm port object. If a port is given, then the port will be
           opened immediately. Otherwise a Serial port object in closed state
           is returned."""

        self._isOpen   = False
        self._port     = None           # correct value is assigned below through properties
        self._baudrate = None           # correct value is assigned below through properties
        self._bytesize = None           # correct value is assigned below through properties
        self._parity   = None           # correct value is assigned below through properties
        self._stopbits = None           # correct value is assigned below through properties
        self._timeout  = None           # correct value is assigned below through properties
        self._writeTimeout = None       # correct value is assigned below through properties
        self._xonxoff  = None           # correct value is assigned below through properties
        self._rtscts   = None           # correct value is assigned below through properties
        self._dsrdtr   = None           # correct value is assigned below through properties
        self._interCharTimeout = None   # correct value is assigned below through properties

        # assign values using get/set methods using the properties feature
        self.port     = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity   = parity
        self.stopbits = stopbits
        self.timeout  = timeout
        self.writeTimeout = writeTimeout
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self.dsrdtr   = dsrdtr
        self.interCharTimeout = interCharTimeout

        self.open()

    def isOpen(self):
        """Check if the port is opened."""
        return self._isOpen

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    # TODO: these are not really needed as the is the BAUDRATES etc. attribute...
    # maybe i remove them before the final release...

    def getSupportedBaudrates(self):
        return [(str(b), b) for b in self.BAUDRATES]

    def getSupportedByteSizes(self):
        return [(str(b), b) for b in self.BYTESIZES]

    def getSupportedStopbits(self):
        return [(str(b), b) for b in self.STOPBITS]

    def getSupportedParities(self):
        return [(PARITY_NAMES[b], b) for b in self.PARITIES]

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def setPort(self, port):
        """Change the port. The attribute portstr is set to a string that
           contains the name of the port."""

        was_open = self._isOpen
        if was_open: self.close()
        if port is not None:
            if isinstance(port, basestring):
                self.portstr = port
            else:
                self.portstr = self.makeDeviceName(port)
        else:
            self.portstr = None
        self._port = port
        self.name = self.portstr
        if was_open: self.open()

    def getPort(self):
        """Get the current port setting. The value that was passed on init or using
           setPort() is passed back. See also the attribute portstr which contains
           the name of the port as a string."""
        return self._port

    port = property(getPort, setPort, doc="Port setting")


    def setBaudrate(self, baudrate):
        """Change baud rate. It raises a ValueError if the port is open and the
        baud rate is not possible. If the port is closed, then the value is
        accepted and the exception is raised when the port is opened."""
        try:
            b = int(baudrate)
        except TypeError:
            raise ValueError("Not a valid baudrate: %r" % (baudrate,))
        else:
            if b <= 0:
                raise ValueError("Not a valid baudrate: %r" % (baudrate,))
            self._baudrate = b
            if self._isOpen:  self._reconfigurePort()

    def getBaudrate(self):
        """Get the current baud rate setting."""
        return self._baudrate

    baudrate = property(getBaudrate, setBaudrate, doc="Baud rate setting")


    def setByteSize(self, bytesize):
        """Change byte size."""
        if bytesize not in self.BYTESIZES: raise ValueError("Not a valid byte size: %r" % (bytesize,))
        self._bytesize = bytesize
        if self._isOpen: self._reconfigurePort()

    def getByteSize(self):
        """Get the current byte size setting."""
        return self._bytesize

    bytesize = property(getByteSize, setByteSize, doc="Byte size setting")


    def setParity(self, parity):
        """Change parity setting."""
        if parity not in self.PARITIES: raise ValueError("Not a valid parity: %r" % (parity,))
        self._parity = parity
        if self._isOpen: self._reconfigurePort()

    def getParity(self):
        """Get the current parity setting."""
        return self._parity

    parity = property(getParity, setParity, doc="Parity setting")


    def setStopbits(self, stopbits):
        """Change stop bits size."""
        if stopbits not in self.STOPBITS: raise ValueError("Not a valid stop bit size: %r" % (stopbits,))
        self._stopbits = stopbits
        if self._isOpen: self._reconfigurePort()

    def getStopbits(self):
        """Get the current stop bits setting."""
        return self._stopbits

    stopbits = property(getStopbits, setStopbits, doc="Stop bits setting")


    def setTimeout(self, timeout):
        """Change timeout setting."""
        if timeout is not None:
            try:
                timeout + 1     # test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % (timeout,))
            if timeout < 0: raise ValueError("Not a valid timeout: %r" % (timeout,))
        self._timeout = timeout
        if self._isOpen: self._reconfigurePort()

    def getTimeout(self):
        """Get the current timeout setting."""
        return self._timeout

    timeout = property(getTimeout, setTimeout, doc="Timeout setting for read()")


    def setWriteTimeout(self, timeout):
        """Change timeout setting."""
        if timeout is not None:
            if timeout < 0: raise ValueError("Not a valid timeout: %r" % (timeout,))
            try:
                timeout + 1     #test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % timeout)

        self._writeTimeout = timeout
        if self._isOpen: self._reconfigurePort()

    def getWriteTimeout(self):
        """Get the current timeout setting."""
        return self._writeTimeout

    writeTimeout = property(getWriteTimeout, setWriteTimeout, doc="Timeout setting for write()")


    def setXonXoff(self, xonxoff):
        """Change XON/XOFF setting."""
        self._xonxoff = xonxoff
        if self._isOpen: self._reconfigurePort()

    def getXonXoff(self):
        """Get the current XON/XOFF setting."""
        return self._xonxoff

    xonxoff = property(getXonXoff, setXonXoff, doc="XON/XOFF setting")

    def setRtsCts(self, rtscts):
        """Change RTS/CTS flow control setting."""
        self._rtscts = rtscts
        if self._isOpen: self._reconfigurePort()

    def getRtsCts(self):
        """Get the current RTS/CTS flow control setting."""
        return self._rtscts

    rtscts = property(getRtsCts, setRtsCts, doc="RTS/CTS flow control setting")

    def setDsrDtr(self, dsrdtr=None):
        """Change DsrDtr flow control setting."""
        if dsrdtr is None:
            # if not set, keep backwards compatibility and follow rtscts setting
            self._dsrdtr = self._rtscts
        else:
            # if defined independently, follow its value
            self._dsrdtr = dsrdtr
        if self._isOpen: self._reconfigurePort()

    def getDsrDtr(self):
        """Get the current DSR/DTR flow control setting."""
        return self._dsrdtr

    dsrdtr = property(getDsrDtr, setDsrDtr, "DSR/DTR flow control setting")

    def setInterCharTimeout(self, interCharTimeout):
        """Change inter-character timeout setting."""
        if interCharTimeout is not None:
            if interCharTimeout < 0: raise ValueError("Not a valid timeout: %r" % interCharTimeout)
            try:
                interCharTimeout + 1     # test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % interCharTimeout)

        self._interCharTimeout = interCharTimeout
        if self._isOpen: self._reconfigurePort()

    def getInterCharTimeout(self):
        """Get the current inter-character timeout setting."""
        return self._interCharTimeout

    interCharTimeout = property(getInterCharTimeout, setInterCharTimeout, doc="Inter-character timeout setting for read()")

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    _SETTINGS = ('baudrate', 'bytesize', 'parity', 'stopbits', 'xonxoff',
            'dsrdtr', 'rtscts', 'timeout', 'writeTimeout', 'interCharTimeout')

    def getSettingsDict(self):
        """Get current port settings as a dictionary. For use with
        applySettingsDict"""
        return dict([(key, getattr(self, '_'+key)) for key in self._SETTINGS])

    def applySettingsDict(self, d):
        """apply stored settings from a dictionary returned from
        getSettingsDict. it's allowed to delete keys from the dictionary. these
        values will simply left unchanged."""
        for key in self._SETTINGS:
            if d[key] != getattr(self, '_'+key):   # check against internal "_" value
                setattr(self, key, d[key])          # set non "_" value to use properties write function

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def __repr__(self):
        """String representation of the current port settings and its state."""
        return "%s<id=0x%x, open=%s>(port=%r, baudrate=%r, bytesize=%r, parity=%r, stopbits=%r, timeout=%r, xonxoff=%r, rtscts=%r, dsrdtr=%r)" % (
            self.__class__.__name__,
            id(self),
            self._isOpen,
            self.portstr,
            self.baudrate,
            self.bytesize,
            self.parity,
            self.stopbits,
            self.timeout,
            self.xonxoff,
            self.rtscts,
            self.dsrdtr,
        )


    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # compatibility with io library

    def readable(self): return True
    def writable(self): return True
    def seekable(self): return False
    def readinto(self, b):
        data = self.read(len(b))
        n = len(data)
        try:
            b[:n] = data
        except TypeError, err:
            import array
            if not isinstance(b, array.array):
                raise err
            b[:n] = array.array('b', data)
        return n


class FTDISerial(SerialBase):
    """
    Make FTDI lib look like a pyserial device.

    Arguments:
        Port: should eventually take a VID/PID/Interface string
    """

    def open(self):
        if(self.port == None):
            print "opening first available ftdi device..."
        else:
            print "opening ftdi device with serial %s" % self.port

        try:
            self._ftdi_dev = pylibftdi.Device(device_id=self.port, mode='t', interface_select=pylibftdi.INTERFACE_B)
        except:
            raise
            
        self._reconfigurePort()
        self._isOpen = True

    def _reconfigurePort(self):
        self._ftdi_dev.baudrate = self._baudrate

    def close(self):
        self._ftdi_dev.close()

    def read(self, size=1):
        """
        Read size bytes from the serial port. No timeout (unlike pyserial).

        Returns: bytes read from port.
        """
        return self._ftdi_dev.read(size)

    def write(self, data):
        """
        Write the string data to the port.

        Returns: number of bytes written.
        """
        return self._ftdi_dev.write(data)

    def inWaiting(self):
        """
        Return the number of chars in the receive buffer. Not actually implemented.
        """
        return 0

    def flush(self):
        """
        Flush of file like objects. In this case, wait until all data is written.
        """
        self._ftdi_dev.flush()

    def flushInput():
        """
        Flush input buffer, discarding all it's contents.
        """
        self._ftdi_dev.flush_input()

    def flushOutput():
        """
        Clear output buffer, aborting the current output and discarding all that is in the buffer.
        """
        self._ftdi_dev.flush_output()

    def sendBreak(duration=0.25):
        """
        Send break condition. Timed, returns to idle state after given duration. Not implemented.
        """
        pass

    def setBreak(level=True):
        """
        Set break: Controls TXD. When active, no transmitting is possible. Not implemented.
        """
        pass

    def setRTS(level=True):
        """
        Set RTS line to specified logic level.
        """
        self._ftdi_dev.rts = level

    def setDTR(level=True):
        """
        Set DTR line to specified logic level.
        """
        self._ftdi_dev.dtr = level

    def getCTS():
        """
        Return the state of the CTS line.
        """
        return self._ftdi_dev.cts

    def getDSR():
        """
        Return the state of the DSR line.
        """
        return self._ftdi_dev.dsr

    def getRI():
        """
        Return the state of the RI line.
        """
        return self._ftdi_dev.ri

    def getCD():
        """
        Return the state of the CD line.
        """
        return 0

    
