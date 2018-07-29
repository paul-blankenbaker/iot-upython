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
    wlan = network.WLAN(network.STA_IF)
    # Set name to provide to DHCP server here to help
    # find your IOT device on the LAN
    wlan.config(dhcp_hostname='queso')
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        # Change to SSID/PASSWORD for your AP
        wlan.connect('SSID', 'WPA2_PASSWORD')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

# Make sure we are connected
do_connect()

# Enable REPL interface access using browser and WebREPL
webrepl.start()

# Initial garbage collection
gc.collect()
