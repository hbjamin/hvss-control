#!/usr/bin/python

# Copyright 2012 Daniel Berlin (with some changes by Adafruit Industries/Limor Fried)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal  MCP230XX_GPIO(1, 0xin
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from Adafruit_I2C import Adafruit_I2C
import smbus
import time


#Uncomment for MCP2016
#******************************
MCP230xx_IODIRA = 0x06
MCP230xx_IODIRB = 0x07
MCP230xx_GPIOA  = 0x00
MCP230xx_GPIOB  = 0x01
MCP230xx_IPOLA  = 0x04
MCP230xx_IPOLB  = 0x05
MCP230xx_OLATA  = 0x02
MCP230xx_OLATB  = 0x03
#******************************
'''
#Uncomment for MCP2017
#******************************
MCP230xx_IODIRA = 0x00
MCP230xx_IODIRB = 0x01
MCP230xx_GPIOA  = 0x12
MCP230xx_GPIOB  = 0x13
MCP230xx_GPPUA  = 0x0C
MCP230xx_GPPUB  = 0x0D
MCP230xx_OLATA  = 0x14
MCP230xx_OLATB  = 0x15
#*****************************
'''
MCP23008_GPIOA  = 0x09
MCP23008_GPPUA  = 0x06
MCP23008_OLATA  = 0x0A

OUT = 0x00
IN  = 0xFF

class Adafruit_MCP230XX(object):
    OUTPUT = 0
    INPUT = 1
    def __init__(self, address, num_gpios, busnum=-1, PortDir_default = OUT):
        assert num_gpios >= 0 and num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        self.i2c = Adafruit_I2C(address=address, debug=True)
        self.address = address
        print("     address is now set to: ",self.address,hex(self.address))
        time.sleep(1)
        self.num_gpios = num_gpios
        self.portdir = PortDir_default
        self.direction = -2;

    def setDirection(self):
         # set directions
        # set defaults
        if self.num_gpios <= 8:
            self.i2c.write8(MCP230xx_IODIRA, self.portdir)  # all inputs on port A
            self.direction = self.i2c.readU8(MCP230xx_IODIRA)
            self.i2c.write8(MCP23008_GPPUA, 0x00)
        elif self.num_gpios > 8 and self.num_gpios <= 16:
            # The function write8(reg,val) writes to self.address

            print("     address: ",self.address," register:",MCP230xx_IODIRA," value of: ",self.portdir)



            dataOut = [self.portdir,self.portdir]
            dataIn = [0,0]

            self.i2c.writeList(MCP230xx_IODIRA,dataOut)
            #self.i2c.writeList(MCP230xx_IODIRA, self.portdir)  # all inputs on port A

            print("     writing to register:",MCP230xx_IODIRB," a value of: ",self.portdir)
            self.i2c.write8(MCP230xx_IODIRB, self.portdir)  # all inputs on port B

            print("     setting self.direction to: ",self.i2c.readU8(MCP230xx_IODIRA)," - the value read from register: ",MCP230xx_IODIRA)
            self.direction = self.i2c.readU8(MCP230xx_IODIRA)

            print("     setting self.direction to: ",self.i2c.readU8(MCP230xx_IODIRB)," - the value read from register: ",MCP230xx_IODIRB)
            self.direction |= self.i2c.readU8(MCP230xx_IODIRB) << 8

            print("FOR DIR A - DIRECTION REG=",self.direction,self.portdir)
            print("FOR DIR B - DIRECTION REG=",self.direction,self.portdir)
            #self.i2c.write8(MCP230xx_GPPUA, 0x00)
            #self.i2c.write8(MCP230xx_GPPUB, 0x00)



    def _changebit(self, bitmap, bit, value):
        assert value == 1 or value == 0, "Value is %s must be 1 or 0" % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _readandchangepin(self, port, pin, value, currvalue = None):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        #assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        if not currvalue:
             currvalue = self.i2c.readU8(port)
        newvalue = self._changebit(currvalue, pin, value)
        self.i2c.write8(port, newvalue)
        return newvalue


    def pullup(self, pin, value):
        if self.num_gpios <= 8:
            return self._readandchangepin(MCP23008_GPPUA, pin, value)
        if self.num_gpios <= 16:
            lvalue = self._readandchangepin(MCP230xx_IPOLA, pin, value)
            if (pin < 8):
                return
            else:
                return self._readandchangepin(MCP230xx_IPOLB, pin-8, value) << 8

    # Set pin to either input or output mode
    def config(self, pin, mode):
        if self.num_gpios <= 8:
            self.direction = self._readandchangepin(MCP230xx_IODIRA, pin, mode)
        if self.num_gpios <= 16:
            if (pin < 8):
                self.direction = self._readandchangepin(MCP230xx_IODIRA, pin, mode)
            else:
                self.direction |= self._readandchangepin(MCP230xx_IODIRB, pin-8, mode) << 8

        return self.direction

    def output(self, pin, value):
        # assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        if self.num_gpios <= 8:
            self.outputvalue = self._readandchangepin(MCP23008_GPIOA, pin, value, self.i2c.readU8(MCP23008_OLATA))
        if self.num_gpios <= 16:
            if (pin < 8):
                self.outputvalue = self._readandchangepin(MCP230xx_GPIOA, pin, value, self.i2c.readU8(MCP230xx_OLATA))
            else:
                self.outputvalue = self._readandchangepin(MCP230xx_GPIOB, pin-8, value, self.i2c.readU8(MCP230xx_OLATB)) << 8

        return self.outputvalue


        self.outputvalue = self._readandchangepin(MCP230xx_IODIRA, pin, value, self.outputvalue)
        return self.outputvalue

    def input(self, pin):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input" % pin
        if self.num_gpios <= 8:
            value = self.i2c.readU8(MCP23008_GPIOA)
        elif self.num_gpios > 8 and self.num_gpios <= 16:
            value = self.i2c.readU8(MCP230xx_GPIOA)
            value |= self.i2c.readU8(MCP230xx_GPIOB) << 8
        return value & (1 << pin)

    def readU8(self):
        result = self.i2c.readU8(MCP23008_OLATA)
        return(result)

    def readS8(self):
        result = self.i2c.readU8(MCP23008_OLATA)
        if (result > 127): result -= 256
        return result

    def readU16(self):
        assert self.num_gpios >= 16, "16bits required"
        lo = self.i2c.readU8(MCP230xx_OLATA)
        hi = self.i2c.readU8(MCP230xx_OLATB)
        return((hi << 8) | lo)

    def readS16(self):
        assert self.num_gpios >= 16, "16bits required"
        lo = self.i2c.readU8(MCP230xx_OLATA)
        hi = self.i2c.readU8(MCP230xx_OLATB)
        if (hi > 127): hi -= 256
        return((hi << 8) | lo)

    def write8(self, value):
        self.i2c.write8(MCP23008_OLATA, value)

    def write16(self, value):
        assert self.num_gpios >= 16, "16bits required"
        self.i2c.write8(MCP230xx_OLATA, value & 0xFF)
        self.i2c.write8(MCP230xx_OLATB, (value >> 8) & 0xFF)

# RPi.GPIO compatible interface for MCP230xx and MCP23008
'''
class MCP230XX_GPIO(object):
    OUT = 0
    IN = 1
    BCM = 0
    BOARD = 0
    def __init__(self, busnum, address, num_gpios):
        self.chip = Adafruit_MCP230XX(address, num_gpios, busnum)
    def setmode(self, mode):
        # do nothing
        pass
    def setup(self, pin, mode):
        self.chip.config(pin, mode)
    def input(self, pin):
        return self.chip.input(pin)
    def output(self, pin, value):
        self.chip.output(pin, value)
    def pullup(self, pin, value):
        self.chip.pullup(pin, value)


if __name__ == '__main__':
    # ***************************************************
    # Set num_gpios to 8 for MCP23008 or 16 for MCP23017!
    # ***************************************************
    mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 8) # MCP23008
    # mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 16) # MCP23017

    # Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
    mcp.config(0, mcp.OUTPUT)
    mcp.config(1, mcp.OUTPUT)
    mcp.config(2, mcp.OUTPUT)

    # Set pin 3 to input with the pullup resistor enabled
    mcp.config(3, mcp.INPUT)
    mcp.pullup(3, 1)

    # Read input pin and display the results
    print( "Pin 3 = %d" % (mcp.input(3) >> 3))

    # Python speed test on output 0 toggling at max speed
    print ("Starting blinky on pin 0 (CTRL+C to quit)")
    while (True):
      mcp.output(0, 1)  # Pin 0 High
      time.sleep(1);
      mcp.output(0, 0)  # Pin 0 Low
      time.sleep(1);
      print( "Pin 3 = %d" % (mcp.input(3)))
'''