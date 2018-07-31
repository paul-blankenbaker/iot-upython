# Garage Door Opener

Simple MicroPython application intended for a ESP8266 or ESP32 that:

- Provides a simple web interface with a single button.

- Pressing the button on the web interface triggers an I/O pin to go
  high for about a tenth of a second and then returns back to a low
  state.

- The I/O line is then tied to a relay to trigger the relay to close
  during this tenth second pulse.

- The relay is then put in parallel with a garage door opener switch
  so that the pulse will simulate the pressing the "door bell"
  button that controls the garage door (connecting in parallel allows
  the normal "door bell" button to continue working).


# Installation

1. Choose a ESP8266 or ESP32 (or equivalent board that provides WIFI connectivity and supports MicroPython).
2. Install MicroPython on your board Google for "ESP8266 MicroPython" change ESP8266 to match your board. For ESP8266: <https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html> was a good reference at the time this README.md file was created.
3. Enable the WI-FI access point mode on your board and (optionally) also connect it to your WI-FI network.
4. Copy the main.py file to your board. Optionally, edit the boot.py with settings for your WIFI access point and copy it to your device.
5. Reboot your IOT board.
6. Use your phone or compute to connect to IOT board WI-FI and then open http://192.168.4.1/garage in your web browser.
7. If you set up your board to connect to your local network's WI-FI access point, determine the IP address of the board and connect to it.


# Tips and Tricks

Enable WebREPL for remote access.
* On-line at: <http://micropython.org/webrepl/> (NOTE: Browser may prevent you using if open in https).
* Download at: <https://github.com/micropython/webrepl>

Putty works well on Linux and Windows for accessing via USB/serial
interface (speed 115200). Screen also works well on Linux system (as
long as you remember that is is <Control-A> <k> to exit).

    screen /dev/ttyUSB0 115200

To reboot the ESP8266 using WebREPL or REPL command line:

    import machine
    machine.reset()

To configure Station mode (connect to AP mode):

    import network
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.config(dhcp_hostname='esp32-garage')
    sta.connect('ESSID', 'YOUR_AP_PASSPHRASE')

To configure Access Point (AP mode):

    import network
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='esp32-garage', authmode=network.AUTH_WPA2_PSK, password='YOUR_WPA_PASSPHRASE')
