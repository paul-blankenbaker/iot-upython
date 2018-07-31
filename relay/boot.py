# This file is executed on every boot (including wake-boot from deepsleep)
#
# - Verifies that you are connected to WIFI AP (or connects if not)
# - Enables REPL access via web browers using WebREPL interface (see:
#   https://github.com/micropython/webrepl)

#import esp
#esp.osdebug(None)
import gc
import webrepl

# Helper method to make sure we are connected to the network
def do_connect():
    import network
    name = 'esp32-garage'
    essid = 'YOUR_AP_ESSID'
    passPhrase = 'YOUR_WPA2_PASSPHRASE'

    try:
        sta = network.WLAN(network.STA_IF)
        # Set name to provide to DHCP server here to help
        # find your IOT device on the LAN
        sta.config(dhcp_hostname=name)
        sta.active(True)
        if not sta.isconnected():
            print('connecting to network...')
            # Change to SSID/PASSWORD for your AP
            sta.connect(essid, passPhrase)
            while not sta.isconnected():
                pass
            print('network config:', sta.ifconfig())
    except Exception as err:
        print('Exception setting up STA mode: ', err)

    try:
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=name, authmode=network.AUTH_WPA2_PSK, password=passPhrase)
    except Exception as err:
        print('Exception setting up AP mode: ', err)

# Make sure we are connected
do_connect()

# Enable REPL interface access using browser and WebREPL
webrepl.start()

# Initial garbage collection
gc.collect()
