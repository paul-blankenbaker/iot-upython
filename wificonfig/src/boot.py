from wificonfig import setupWifi
import webrepl
import gc

setupWifi(requireAp=True, requireSta=True)
webrepl.start()
# Initial garbage collection
gc.collect()

# To debug WIFI config HTTP server
#import wificonfigserver
#wificonfigserver.runServer()

