import json
import network

# These will be set to network.WLAN objects depending on
# configuration and success at setup, you can test/use
# them as you want after running setupWifi()
ap = None
sta = None

# This method attempts to configure both WIFI AP and Station
# modes of ESP32 (depending on configuration).
#
# cfg - A Python dictionary. The dictionary can be empty as we will
# supply default values for missing entries (they probably won't
# be what you want):
#
# enableAp (True)
#   If True, we will try to enable AP mode (requires ssidAp).
# ssidAp ("esp32-ap")
#   SSID to use for AP Mode (what we broadcast).
# enableSta (False)
#   If True, we will try to enable Station mode (requires ssidSta).
#
#  
def attemptSetup(cfg):
    global ap
    global sta

    ap = None
    sta = None

    #print(cfg)
    ssid = cfg.get("ssidAp", "esp32-ap")
    if ssid != "" and cfg.get("enableAp", True):
        _ap = network.WLAN(network.AP_IF)
        _ap.active(True)
        psk = cfg.get("pskAp", "")
        if psk != "":
            _ap.config(essid=ssid, authmode=network.AUTH_WPA2_PSK, password=psk)
        else:
            _ap.config(essid=ssid, authmode=network.AUTH_OPEN)
        print(ssid, ' AP config:', _ap.ifconfig())
        # At this point consider AP active
        ap = _ap
    
    ssid = cfg.get("ssidSta", "")
    if ssid != "" and cfg.get("enableSta", False):
        _sta = network.WLAN(network.STA_IF)
        name = cfg.get("nameSta", "")
        if name != "":
            _sta.config(dhcp_hostname=name)
        _sta.active(True)
        if not _sta.isconnected():
            psk = cfg.get("pskSta", "")
            print('connecting to ', ssid, ' ...')
            # Change to SSID/PASSWORD for your AP
            if psk != "":
                _sta.connect(ssid, psk)
            else:
                _sta.connect(ssid)

            import time
            startTime = time.time()
            timeout = float(cfg.get("timeoutSta", 10))

            while not _sta.isconnected():
                if (time.time() - startTime) >= timeout:
                    break

            if _sta.isconnected():
                # At this point, consider ourselves connected
                sta = _sta
                print(ssid, ' network config:', _sta.ifconfig())
            else:
                print(ssid, " gave up on establishing connection")
                _sta.disconnect()

def setupWifi(requireAp=True, requireSta=False):
    global ap
    global sta

    try:
        with open('wificonfig.json') as jsonFile:
            cfg = json.load(jsonFile)
        attemptSetup(cfg)
    except Exception as err:
        print("Problem with WIFI configuration", err)

    if (requireAp and (ap == None)) or (requireSta and (sta == None)):
        if (ap == None) and (sta == None):
            print("Neither WIFI AP or Station mode configured using defaults")
            cfg = { }
            attemptSetup(cfg)
        import os
        from machine import WDT
        # Give 5 minutes to configure WIFI before resetting and trying again
        # (handles case where access point happened to be down when this
        # system came up)
        WDT(timeout=300000)
        # No os.path in upython
        if "wificonfigserver.py" in os.listdir():
            from wificonfigserver import runServer
            runServer()
        else:
            # Make an attempt to start up webrepl for
            # file transfer
            import webrepl
            webrepl.start()
