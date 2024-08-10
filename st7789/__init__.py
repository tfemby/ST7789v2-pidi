# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import numbers
import time

import gpiod
import gpiodevice
import numpy
import spidev
from gpiod.line import Direction, Value

__version__ = "1.0.1"

OUTL = gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)

BG_SPI_CS_BACK = 0
BG_SPI_CS_FRONT = 1

SPI_CLOCK_HZ = 16000000

ST7789_NOP = 0x00
ST7789_SWRESET = 0x01
ST7789_RDDID = 0x04
ST7789_RDDST = 0x09

ST7789_SLPIN = 0x10
ST7789_SLPOUT = 0x11
ST7789_PTLON = 0x12
ST7789_NORON = 0x13

ST7789_INVOFF = 0x20
ST7789_INVON = 0x21
ST7789_DISPOFF = 0x28
ST7789_DISPON = 0x29

ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_RAMRD = 0x2E

ST7789_PTLAR = 0x30
ST7789_MADCTL = 0x36
ST7789_COLMOD = 0x3A

ST7789_RAMCTRL = 0xB0 # RAM Control
ST7789_FRMCTR1 = 0xB1 # RGBCTRL
ST7789_FRMCTR2 = 0xB2 # PORCTRL
ST7789_FRMCTR3 = 0xB3 # FRCTRL1
#ST7789_INVCTR = 0xB4
ST7789_PARCTRL = 0xB5
ST7789_DISSET5 = 0xB6

ST7789_GCTRL = 0xB7 # Gate Control
ST7789_GTADJ = 0xB8 # Gate on Timing Adjustment
ST7789_DGMEN = 0xBA # Digital Gamma Enable
ST7789_VCOMS = 0xBB # VCOM Setting
ST7789_POWERSAVE = 0xBC # Power Saving Mode
ST7789_DLPOFFSAVE = 0xBD # Display Off Power Save

ST7789_LCMCTRL = 0xC0 # LCM Control
ST7789_IDSET = 0xC1 # ID Code Setting
ST7789_VDVVRHEN = 0xC2 # VDV and VRH Command Enable
ST7789_VRHS = 0xC3 # VRH Set
ST7789_VDVS = 0xC4 # VDV Set
ST7789_VMCTR1 = 0xC5 # VCMOSFET: VCOM Offset Set
ST7789_FRCTRL2 = 0xC6 # Frame Rate Control in Normal Mode
ST7789_CABCCTRL = 0xC7 # CBAC Control
ST7789_REGSEL1 = 0xC8 # Register Value Selection 1
ST7789_REGSEL2 = 0xCA # Register Value Selection 2

ST7789_PWNFRSEL = 0xCC # PWM Frequency Selection
ST7789_PWRCTRL1 = 0xD0 # Power Control 1
ST7789_VAPVANEN = 0xD2 # Enable VAP/VAN signal output
ST7789_CMD2EN = 0xDF # Command 2 Enable

ST7789_RDID1 = 0xDA
ST7789_RDID2 = 0xDB
ST7789_RDID3 = 0xDC
ST7789_RDID4 = 0xDD

ST7789_GMCTRP1 = 0xE0 # PVGAMCTRL: Positive Voltage Gamma Control
ST7789_GMCTRN1 = 0xE1 # NVGAMCTRL: Negative Voltage Gamma Control
ST7789_DGMLUTR = 0xE2 # Digital Gamma Look-up Table for Red
ST7789_DGMLUTB = 0xE3 # Digital Gamma Look-up Table for Blue

ST7789_GATECTRL = 0xE4 # Gate Control
ST7789_SPI2EN = 0xE7 # SPI2 Enable
ST7789_PWCTRL2 = 0xE8 # Power Control 2
ST7789_EQCTRL = 0xE9 # Equalize Time Control
ST7789_PROMTRL = 0xEC # Program Mode Control
ST7789_PROMEN = 0xFA # Program Mode Enable
ST7789_NVMSET = 0xFC # NVM address Setting
ST7789_PROMACT = 0xFE # Program Action (needs to be set when Program mode is enabled)

ST7789_PWCTR6 = 0xFC


class ST7789(object):
    """Representation of a ST7789v2 TFT LCD."""

    def __init__(
        self,
        port,
        cs,
        dc,
        backlight=None,
        rst=None,
        width=240,
        height=320,
        rotation=0,
        invert=True,
        spi_speed_hz=4000000,
        offset_left=0,
        offset_top=0,
    ):
        """Create an instance of the display using SPI communication.

        Must provide the GPIO pin number for the D/C pin and the SPI driver.

        Can optionally provide the GPIO pin number for the reset pin as the rst parameter.

        :param port: SPI port number
        :param cs: SPI chip-select number (0 or 1 for BCM
        :param backlight: Pin for controlling backlight
        :param rst: Reset pin for ST7789
        :param width: Width of display connected to ST7789
        :param height: Height of display connected to ST7789
        :param rotation: Rotation of display connected to ST7789
        :param invert: Invert display
        :param spi_speed_hz: SPI speed (in Hz)

        """
        if rotation not in [0, 90, 180, 270]:
            raise ValueError(f"Invalid rotation {rotation}")

        if width != height and rotation in [90, 270]:
            raise ValueError(
                f"Invalid rotation {rotation} for {width}x{height} resolution"
            )

        gpiodevice.friendly_errors = True

        self._spi = spidev.SpiDev(port, cs)
        self._spi.mode = 0
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = spi_speed_hz

        self._dc = dc
        self._rst = rst
        self._width = width
        self._height = height
        self._rotation = rotation
        self._invert = invert

        self._offset_left = offset_left
        self._offset_top = offset_top

        # Set DC as output.
        self._dc = gpiodevice.get_pin(dc, "st7789-dc", OUTL)

        # Setup backlight as output (if provided).
        if backlight is not None:
            self._bl = gpiodevice.get_pin(backlight, "st7789-bl", OUTL)
            self.set_pin(self._bl, False)
            time.sleep(0.1)
            self.set_pin(self._bl, True)

        # Setup reset as output (if provided).
        if rst is not None:
            self._rst = gpiodevice.get_pin(rst, "st7789-rst", OUTL)
            self.reset()

        self._init()

    def set_pin(self, pin, state):
        lines, offset = pin
        lines.set_value(offset, Value.ACTIVE if state else Value.INACTIVE)

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        self.set_pin(self._dc, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.xfer(data[start:end])

    def set_backlight(self, value):
        """Set the backlight on/off."""
        if self._bl is not None:
            self.set_pin(self._bl, value)

    @property
    def width(self):
        return (
            self._width
            if self._rotation == 0 or self._rotation == 180
            else self._height
        )

    @property
    def height(self):
        return (
            self._height
            if self._rotation == 0 or self._rotation == 180
            else self._width
        )

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            self.set_pin(self._rst, True)
            time.sleep(0.500)
            self.set_pin(self._rst, False)
            time.sleep(0.500)
            self.set_pin(self._rst, True)
            time.sleep(0.500)

    def _init(self):
        # Initialize the display.

        self.command(ST7789_SWRESET)  # Software reset
        time.sleep(0.150)  # delay 150 ms

        self.command(ST7789_MADCTL)
        self.data(0x00)

        self.command(ST7789_COLMOD)  # Frame rate ctrl - idle mode
        self.data(0x05)

        self.command(ST7789_FRMCTR2)
        self.data(0x0B)
        self.data(0x0B)
        self.data(0x00)
        self.data(0x33)
        self.data(0x35)

        self.command(ST7789_GCTRL)
        self.data(0x11)

        self.command(ST7789_VCOMS)
        self.data(0x35)

        self.command(ST7789_LCMCTRL)  # Power control
        self.data(0x2C)

        self.command(ST7789_VDVVRHEN)  # Power control
        self.data(0x01)

        self.command(ST7789_VRHS)  # Power control
        self.data(0x0D)

        self.command(ST7789_VDVS)  # Power control
        self.data(0x20)

        self.command(ST7789_FRCTRL2)
        self.data(0x13)
        
        self.command(ST7789_PWRCTRL1)
        self.data(0xA4)
        self.data(0xA1)

        self.command(0xD6)
        self.data(0xA1)

        self.command(ST7789_GMCTRP1)  # Set Gamma
        self.data(0xF0)
        self.data(0x06)
        self.data(0x0B)
        self.data(0x0A)
        self.data(0x09)
        self.data(0x26)
        self.data(0x29)
        self.data(0x33)
        self.data(0x41)
        self.data(0x18)
        self.data(0x16)
        self.data(0x15)
        self.data(0x29)
        self.data(0x2D)

        self.command(ST7789_GMCTRN1)  # Set Gamma
        self.data(0xF0)
        self.data(0x04)
        self.data(0x08)
        self.data(0x08)
        self.data(0x07)
        self.data(0x03)
        self.data(0x28)
        self.data(0x32)
        self.data(0x40)
        self.data(0x3B)
        self.data(0x19)
        self.data(0x18)
        self.data(0x2A)
        self.data(0x2E)

        if self._invert:
            self.command(ST7789_INVON)  # Invert display
        else:
            self.command(ST7789_INVOFF)  # Don't invert display

        self.command(ST7789_SLPOUT)

        self.command(ST7789_DISPON)  # Display on
        time.sleep(0.100)  # 100 ms

    def begin(self):
        """Set up the display

        Deprecated. Included in __init__.

        """
        pass

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.command(ST7789_CASET)  # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)  # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)  # XEND
        self.command(ST7789_RASET)  # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)  # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)  # YEND
        self.command(ST7789_RAMWR)  # write to RAM

    def display(self, image):
        """Write the provided image to the hardware.

        :param image: Should be RGB format and the same dimensions as the display hardware.

        """
        # Set address bounds to entire display.
        self.set_window()

        # Convert image to 16bit RGB565 format and
        # flatten into bytes.
        pixelbytes = self.image_to_data(image, self._rotation)

        # Write data to hardware.
        for i in range(0, len(pixelbytes), 4096):
            self.data(pixelbytes[i : i + 4096])

    def image_to_data(self, image, rotation=0):
        if not isinstance(image, numpy.ndarray):
            image = numpy.array(image.convert("RGB"))

        # Rotate the image
        pb = numpy.rot90(image, rotation // 90).astype("uint16")

        # Mask and shift the 888 RGB into 565 RGB
        red = (pb[..., [0]] & 0xF8) << 8
        green = (pb[..., [1]] & 0xFC) << 3
        blue = (pb[..., [2]] & 0xF8) >> 3

        # Stick 'em together
        result = red | green | blue

        # Output the raw bytes
        return result.byteswap().tobytes()
