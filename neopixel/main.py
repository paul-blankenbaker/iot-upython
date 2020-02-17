# Some sample code to control NeoPixels using an ESP32
#

import machine
import neopixel
import time

def wheel(pos):
  # Input a value 0 to 255 to get a color value.
  # The colours are a transition r - g - b - back to r.
  if pos < 0 or pos > 255:
    return (0, 0, 0)
  if pos < 85:
    return (255 - pos * 3, pos * 3, 0)
  if pos < 170:
    pos -= 85
    return (0, 255 - pos * 3, pos * 3)
  pos -= 170
  return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(np, wait):
  n = np.n
  for j in range(255):
    for i in range(n):
      rc_index = (i * 256 // n) + j
      np[i] = wheel(rc_index & 255)
    np.write()
    time.sleep_ms(wait)

def cycle(np):
    n = np.n
    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(25)

def fade(np):
    n = np.n
    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
        time.sleep_ms(2)

def set(np, color):
    # clear
    for i in range(np.n):
        np[i] = color
    np.write()

def off(np):
    set(np, (0, 0, 0))

def cycle(np, color):
    n = np.n
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = color
        np.write()
        time.sleep_ms(25)

def bounce(np, color):
    n = np.n
    for i in range(4 * n):
        for j in range(n):
            np[j] = color
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

def fade(np):
    n = np.n
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
        time.sleep_ms(2)

def demo(np):
    cycle(np, (255, 0, 0))
    bounce(np, (0, 0, 128))
    fade(np)
    rainbow_cycle(np, 10)
    off(np)

def demoForever(pin, ledCnt):
    np = neopixel.NeoPixel(machine.Pin(pin), ledCnt)
    while True:
        demo(np)
        time.sleep_ms(3000)

def demoOnce(pin, ledCnt):
    np = neopixel.NeoPixel(machine.Pin(pin), ledCnt)
    demo(np)
    return np

# np = demoOnce(5, 5)
# demoForever(5, 5)
