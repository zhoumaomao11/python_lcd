"""Implements a HD44780 character LCD connected via MCP23008 backpack on I2C bus of Lopy4 board.
   This was tested with: https://www.wemos.cc/product/d1-mini.html"""

from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x20

# Specifically for HD44780 character LCD mounted with MCP23008 backpack
# MCP23008 Registers

IODIR   = 0x00
IPOL    = 0x01
GPINTEN = 0x02
DEFVAL  = 0x03
INTCON  = 0x04
IOCON   = 0x05
GPPU    = 0x06
INTF    = 0x07
INTCAP  = 0x08
GPIO    = 0x09
OLAT    = 0x0A

MASK_RS = 0x02
MASK_E = 0x04
SHIFT_DATA = 3
SHIFT_BACKLIGHT = 7


class I2cLcd(LcdApi):
    """Implements a HD44780 character LCD connected via PCF8574 on I2C."""

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, b'\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00')# modified
        self.i2c.writeto_mem(self.i2c_addr, IODIR, bytearray([0x01]))
        sleep_ms(20)   # Allow LCD time to powerup
        # Send reset 3 times
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(5)    # need to delay at least 4.1 msec
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        # Put LCD into 4 bit mode
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        sleep_ms(1)
        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        """Writes an initialization nibble to the LCD.

        This particular function is only used during initialization.
        """
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
        #self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))	# original
        #self.i2c.writeto(self.i2c_addr, bytearray([byte]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte  | MASK_E]))
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte]))

    def hal_backlight_on(self):
        """Allows the hal layer to turn the backlight on."""
        #self.i2c.writeto(self.i2c_addr, bytearray([1 << SHIFT_BACKLIGHT]))	# original  
        self.i2c.writeto_mem(self.i2c_addr, GPIO, 1 << SHIFT_BACKLIGHT)

    def hal_backlight_off(self):
        """Allows the hal layer to turn the backlight off."""
        #self.i2c.writeto(self.i2c_addr, bytearray([0]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, 0)

    def hal_write_command(self, cmd):
        """Writes a command to the LCD.

        Data is latched on the falling edge of E.
        """
        byte = ((self.backlight << SHIFT_BACKLIGHT) | 
               (((cmd >> 4) & 0x0f) << SHIFT_DATA))
        #self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))	# original
        #self.i2c.writeto(self.i2c_addr, bytearray([byte]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte | MASK_E]))
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte]))
        
        byte = ((self.backlight << SHIFT_BACKLIGHT) | 
               ((cmd & 0x0f) << SHIFT_DATA))
        #self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))	# original
        #self.i2c.writeto(self.i2c_addr, bytearray([byte]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte | MASK_E]))
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte]))
        
        if cmd <= 3:
            # The home and clear commands require a worst case delay of 4.1 msec
            sleep_ms(5)

    def hal_write_data(self, data):
        """Write data to the LCD."""
        byte = (MASK_RS | 
               (self.backlight << SHIFT_BACKLIGHT) | 
               (((data >> 4) & 0x0f) << SHIFT_DATA))
        #self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))	# original
        #self.i2c.writeto(self.i2c_addr, bytearray([byte]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte | MASK_E]))
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte]))
        
        byte = (MASK_RS | 
               (self.backlight << SHIFT_BACKLIGHT) | 
               ((data & 0x0f) << SHIFT_DATA))
        #self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))	# original
        #self.i2c.writeto(self.i2c_addr, bytearray([byte]))	# original
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte | MASK_E]))
        self.i2c.writeto_mem(self.i2c_addr, GPIO, bytearray([byte]))