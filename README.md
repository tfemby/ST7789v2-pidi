# Pidi Modified for ST7789v2

The files have been modified to work with the [1.69inch LCD Module](https://www.waveshare.com/wiki/1.69inch_LCD_Module)
from Waveshare.

This repo is just a fork of the projects created by Pimoroni developers.

- [mopidy-pidi - Mopidy plugin host or pidi display](https://github.com/pimoroni/mopidy-pidi)
- [pidi-plugins - Lower level libraries used to draw to the screen](https://github.com/pimoroni/pidi-plugins)
- [st7789-python - Library to control the ST7789](https://github.com/pimoroni/st7789-python)

I also used sonocottas' fork of the above libraries aimed at making non-square ST7789 based LCD's more compatible
with Orange Pi.

- [pidi-plugins-python](https://github.com/sonocotta/pidi-plugins-python)
- [mopidy-orangepi-pidi](https://github.com/sonocotta/mopidy-orangepi-pidi)
- [st7789-orangepi-python](https://github.com/sonocotta/st7789-orangepi-python)

Please support and look through the original source code. The original authors deserve your support.
I truthfully would've spent a lot longer getting my streamer to workif I needed to write this stack from scratch.

## Changes Made Here
This stack is mostly the same as sonocottas' OrangePi fork. There are some differences in the ST7789 file
regarding the screen initalisation. The code I based this off of was the code provided by waveshare in their
demo for the LCD and verifying that the LCD commands were correct from looking up the ST7789v2 spec sheet.

I've further added some extra commands into the above file that may be useful for people wanting to more deeply
hack their screen.

The other difference is within the pidi\_display\_pil's `__init__` file. The "Artist" section of the screen
buffer was mostly off the top of the screen. I adjusted the canvas margin multiplier so that it looks and
functions correctly.
