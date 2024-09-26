import sys
import math
import time
from Adafruit_I2C import Adafruit_I2C
import RPi.GPIO as GPIO

'''
This script sets the nhit comparator output width for one channel on one board
ARGUMENTS: <Slot#From0> <Channel#From0> <Voltage>
NOTE: Found 1.7V creates the maximum width 
'''

class PiControl():
    def __init__(self,slot,channel,voltage):
        # Pin definitions 
        self.slot_pin=[14,17,27,23,10,25,8,5,12,19,26]  
        self.clear_pin=21 
        # DAC definitions
        self.dac_address=[0x48,0x49,0x4A,0x4B,0x4C,0x4D]
        # Pin setup
        self.SetupPins(slot)
        # DAC setup
        self.dac=self.SetupDAC(channel) 
        # Write to DAC
        self.writeToDAC(channel,voltage)
        # Read from DAC (sanity check)
        self.readFromDAC(channel)
         
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
 
    def SetupDAC(self,channel):
        # Determine which DAC to talk to 
        dac_index=2
        print("Connecting to channel "+str(channel)+"...")
        if channel>7:
            dac_index=3
        print("Connecting to DAC "+str(dac_index)+"...")
        # Start i2c communication with the DAC wanted 
        return Adafruit_I2C(address=self.dac_address[dac_index],debug=True)
 
    def voltageTo10bitDAC(self,voltage):
        # Convert voltage to 10-bit DAC value
        print("Setting threshold to "+str(voltage)+"...")
        print("Converting to 10-bit DAC value...")
        vref=3.3
        bits=10
        resolution=vref/(math.pow(2,bits))
        dac_val=round(voltage/resolution)
        print(dac_val)
        return dac_val
 
    def writeToDAC(self,channel,voltage):
        # Create write command and access byte
        write_ca=0x30+(channel%8) 
        # Create DAC value 
        dac_val=self.voltageTo10bitDAC(voltage)
        # Shift bits to the left
        dac_val=dac_val<<6
        # Split ouput into most and least significant bytes
        dac_data_out=[dac_val>>8,dac_val%256] 
        # Write data to DAC
        print("Writing...") 
        self.dac.writeList(write_ca,dac_data_out)
        time.sleep(0.01)
 
    def readFromDAC(self,channel):
        # Create read command and access byte
        read_ca=0x00+(channel%8)
        print("Reading...")
        self.dac.write8(read_ca,0)
        dac_data_in=self.dac.readList(read_ca,2)
        time.sleep(0.01)

def main():
    if len(sys.argv)!=4:
        print("ERROR! 3 Arguments Required: <Slot#From0> <Channel#From0> <WidthVoltage>")
        sys.exit(1)
    update=PiControl(int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3]))

if __name__=="__main__":
   main() 
