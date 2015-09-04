# FTDITerm

Miniterm (from pyserial) like simple console using the FTDI direct interface. Can be used as an alternative to virtual com ports when you are using a direct driver on a multi-port device. For example, a common use case is the FT2232H with openocd/JTAG on port A and UART on port B. This works sometimes in linux, but OS X and Windows enforce the choice between VPC and D2XX drivers. JTAG and FTDITerm can both use the D2XX interface.

Supports all [libftdi](http://www.intra2net.com/en/developer/libftdi/) supported devices including the FT2232H (testing platform).

Depends on [pylibftdi](https://pypi.python.org/pypi/pylibftdi), which can be installed with pip. pylibftdi depends on the libftdi and libusb libraries.

## Usage

```
% ./ftditerm.py -b 115200 -p asdf
opening ftdi device...
--- Miniterm on asdf: 115200,8,N,1 ---
--- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---

hello world
hello world
hello world

--- exit ---
```

