import sys
import math
import time
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
import RPi.GPIO as GPIO

'''
This script sets the nhit channel mask on one board
The mask can be supplied in either hex or binary
ARGUMENTS: <slot#From0> -h <maskInHex> OR <slot#From0> -b <maskInBinary> 
'''

class PiControl():
    def __init__(self,slot,flag,mask):
        # Pin definitions 
        self.slot_pin=[14,17,27,23,10,25,8,5,12,19,26]  
        self.clear_pin=21 
        # DAC definition
        self.nhit_address=0x25 
        # Pin setup
        self.SetupPins(slot)
        # DAC setup
        self.dac=self.SetupDAC()
        # Check vailidity of mask supplied
        self.CheckMask(flag,mask)
        # Write to DAC
        self.writeToDAC(flag,mask)
        # Read from DAC (sanity check)
        self.readFromDAC()
         
    def SetupPins(self,slot):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # broadcom pin scheme
        for pin in self.slot_pin: # make all slot select pins outputs and deselect them all
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin,GPIO.LOW) 
        GPIO.setup(self.clear_pin,GPIO.OUT) # make clear pin an output
        GPIO.output(self.clear_pin,GPIO.HIGH) # select clear pin
        # Select the slot to update
        print("Connecting to slot "+str(slot)+"...")
        GPIO.output(self.slot_pin[slot],GPIO.HIGH)
 
    def SetupDAC(self):
        print("Connecting to DAC")
        return Adafruit_MCP230XX(address=self.nhit_address,num_gpios=16) 
 
    def CheckMask(self,flag,mask):
        if flag=="-h":
            print("Mask in hex:",mask)
            try: 
                decimal=int(mask,16)
                print("Mask in decimal:",decimal)
                binary=bin(decimal)[2:]
                print("Mask in binary:",binary)
            except ValueError:
                print("Invalid hex number",mask)
                sys.exit(1)
        if flag=="-b":
            print("Mask in binary:",mask)
            try: 
                decimal=int(mask,2)
                print("Mask in decimal:",decimal)
                binary=hex(decimal)[2:].upper()
                print("Mask in hex:",binary)
            except ValueError:
                print("Invalid binary number",mask)
                sys.exit(1)
 
    def writeToDAC(self,flag,mask):
        if flag=="-h":
            print("Writing...")
            print(int(mask,16))
            self.dac.write16(int(mask,16))
        elif flag=="-b":
            print("Writing...") 
            print(int(mask,2))
            self.dac.write16(int(mask,2))
        else:
            print("ERROR! Flag must be either -h for hex or -b for binary")
            sys.exit(1)
        time.sleep(0.01)
 
    def readFromDAC(self):
        print("Reading...")
        print(self.dac.readU16())
        time.sleep(0.01)

def main():
    if len(sys.argv)!=4:
        print("ERROR! 3 Arguments Required: <slot#From0> -h <nhit_mask_hex> OR <slot#From0> -b <nhit_mask_binary>") 
        sys.exit(1)
    update=PiControl(int(sys.argv[1]),sys.argv[2],sys.argv[3])

if __name__=="__main__":
   main() 
