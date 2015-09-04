import pylibftdi

def main():
  with pylibftdi.Device(mode='t', interface_select=pylibftdi.INTERFACE_B) as dev:
    dev.baudrate = 115200
    # dev.write('Hello World')
    while True:
      new_text = dev.readline()
      if(new_text.strip() != ""):
        print(new_text)

if __name__ == "__main__":
  main()
