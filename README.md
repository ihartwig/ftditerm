# FTDITerm

Miniterm (from pyserial) like simple console using the FTDI direct interface. Can be used as an alternative to virtual com ports when you are using a direct driver on a multi-port device. For example, a common use case is the FT2232H with openocd/JTAG on port A and UART on port B. This works sometimes in linux, but OS X and Windows enforce the choice between VPC and D2XX drivers. JTAG and FTDITerm can both use the D2XX interface.

Supports all [libftdi](http://www.intra2net.com/en/developer/libftdi/) supported devices including the FT2232H (testing platform).

Depends on [pylibftdi](https://pypi.python.org/pypi/pylibftdi), which can be installed with pip. pylibftdi depends on the libftdi and libusb libraries.

## Usage

```
% ./ftditerm.py -b 115200
opening first available ftdi device...
--- Miniterm on None: 115200,8,N,1 ---
--- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
hello world
hello world

--- exit ---
```

On linux systems you may need to use `sudo` to access the usb device.

Optionally, use the `-b`/`--baud ` flag to set the baud rate. If not specified, it defaults to 9600.

Optionally, use the `-p`/`--port` flag to look for a specific FTDI serial number. If not specified, use the first one available.

Use `--help` to see the full set of options available.

## Reprogramming USB VID/PID

On Windows/Mac systems the virtual comm port (VCP) driver automatically grab any USB device with the FTDI VID/PID (0x0403/0x6010 for FT2232), blocking access from libusb/libftdi. To prevent auto driver/kext loading we can set the VID to a reserved value (0x0000) and tell our libftdi tools to look for this VID instead. Note that this is not endorsed by USB-IF and should never be done to a production device.

On Linux, just run the `ftdi_usb_program.py` script, probably with `sudo`. Change the `NEW_VID` and `NEW_PID` to your desired values.

On Windows/Mac you will first need to disable the VCP driver. FTDI has documented this for Mac in an [application note (section 7.1)](http://www.ftdichip.com/Support/Documents/AppNotes/AN_134_FTDI_Drivers_Installation_Guide_for_MAC_OSX.pdf). Rename `/System/Library/Extensions/IOUSBFamily.kext/Contents/Plugins/AppleUSBFTDI.kext` to `AppleUSBFTDI.disabled` and reboot. OpenOCD on Windows provides a tool that lets the user change the driver per USB device. Once the VCP driver is disabled, the `ftdi_usb_program.py` script should run successfully. Change the `NEW_VID` and `NEW_PID` to your desired values.
