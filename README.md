# Pidi Modified for ST7789v2

The files have been modified to work with the 1.69inch LCD Module by Waveshare.
[LCD Module](https://www.waveshare.com/wiki/1.69inch_LCD_Module)

This is just a fork of the projects hosted by Pimoroni.

- [mopidy-pidi - Mopidy plugin host or pidi display](https://github.com/pimoroni/mopidy-pidi)
- [pidi-plugins - Lower level libraries used to draw to the screen](https://github.com/pimoroni/pidi-plugins)
- [st7789-python - Library to control the ST7789](https://github.com/pimoroni/st7789-python)

I also used sonocottas' fork of the above libraries aimed at making these more compatible with Orange Pi.

- [pidi-plugins-python](https://github.com/sonocotta/pidi-plugins-python)
- [mopidy-orangepi-pidi](https://github.com/sonocotta/mopidy-orangepi-pidi)
- [st7789-orangepi-python](https://github.com/sonocotta/st7789-orangepi-python)

Please support and look through the original source code that this is derived from and support the developers.
I truthfully would have spent a lot longer if I needed to write this stack from scratch.

This stack is mostly functionally the same as the OrangePi fork. There are some differences in the ST7789 file
regarding the screen initalisation. The code I based this off of was the code provided by waveshare in their
demo for the LCD.

The other difference is within the pidi\_display\_pil `\_\_init\_\_` file. The "Artist" section of the screen
constantly being rendered too high up. I adjusted the canvas margin multiplier so that it fit correctly.
