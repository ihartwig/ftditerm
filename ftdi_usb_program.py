#!/usr/bin/env python

from ctypes import c_int, byref
import pylibftdi
pylibftdi.USB_VID_LIST.append(0x0000)

NEW_VID = 0x0000 # FT2232H: 0x0403
NEW_PID = 0x6010 # FT2232H: 0x6010

VENDOR_ID_FIELD = 0
PRODUCT_ID_FIELD = 1

def main():
  """
  Write the NEW_VID and NEW_PID to any detected FTDI device's eeprom.
  """
  ftdi_dev = pylibftdi.Device(mode='t')

  # read eeprom contents then parse
  ftdi_dev.ftdi_fn.ftdi_read_eeprom()
  ftdi_dev.ftdi_fn.ftdi_eeprom_decode()

  # use library abstraction to get old vid/pid (rather than from the eeprom buffer)
  old_vid = c_int()
  ftdi_dev.ftdi_fn.ftdi_get_eeprom_value(VENDOR_ID_FIELD, byref(old_vid))
  old_pid = c_int()
  ftdi_dev.ftdi_fn.ftdi_get_eeprom_value(PRODUCT_ID_FIELD, byref(old_pid))

  # set new values
  ftdi_dev.ftdi_fn.ftdi_set_eeprom_value(VENDOR_ID_FIELD, NEW_VID)
  ftdi_dev.ftdi_fn.ftdi_set_eeprom_value(PRODUCT_ID_FIELD, NEW_PID)

  # rebuilt the eeprom image to write
  ftdi_dev.ftdi_fn.ftdi_eeprom_build()
  ftdi_dev.ftdi_fn.ftdi_write_eeprom()

  # read back to verify
  ftdi_dev.ftdi_fn.ftdi_read_eeprom()
  ftdi_dev.ftdi_fn.ftdi_eeprom_decode()

  new_vid = c_int()
  ftdi_dev.ftdi_fn.ftdi_get_eeprom_value(VENDOR_ID_FIELD, byref(new_vid))
  new_pid = c_int()
  ftdi_dev.ftdi_fn.ftdi_get_eeprom_value(PRODUCT_ID_FIELD, byref(new_pid))

  print "vid: 0x%x -> 0x%x" % (old_vid.value, new_vid.value)
  print "pid: 0x%x -> 0x%x" % (old_pid.value, new_pid.value)

  if(new_vid.value == NEW_VID and new_pid.value == NEW_PID):
    print "done"
    exit(0)
  else:
    print "could not verify new values!"
    exit(-1)


if __name__ == "__main__":
  main()
