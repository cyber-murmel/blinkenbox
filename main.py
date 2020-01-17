from machine import Pin
from neopixel_spi import NeoPixel
from time import sleep_us

NEO_PIXEL_PIN       = Pin(13, Pin.OUT)
NEO_PIXEL_NUMBER    = 100

hspi = SPI(1, 3200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, mosi=Pin(13))

np = NeoPixel(NEO_PIXEL_PIN, NEO_PIXEL_NUMBER)

