# To test, run this on your ESP32 where you can see the print() output.
# Then use the http://www.hivemq.com/demos/websocket-client/ MQTT client
# to publish messages to the testtopic/1 topic. Each message you publish
# should show up in the REPL output.
#
# LED (Pin 13) on ESP32 should toggle between on/off each time
# a message is received.
#
# NOTE: To install umqtt.robust package on ESP32, run following
# once from REPL prompt:
# import upip
# upip.install('micropython-umqtt.robust')
import machine
import time
import json
from umqtt.robust import MQTTClient

msgRxd = None
msgTime = time.time()

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global msgRxd
    global msgTime
    msgRxd = msg
    msgTime = time.time()

def updateLedState(pin, cnt):
    ledOn = (cnt % 2) == 1
    pin.value(ledOn)
    print("Received message ", cnt, " LED state set to ", ledOn)

def main(server="broker.hivemq.com", topic=b"testtopic/1"):
    global msgRxd
    global msgTime

    msgCnt = 0
    connectOut = machine.Pin(13, machine.Pin.OUT)
    updateLedState(connectOut, msgCnt)
    
    print("Connecting to MQTT server: ", server)
    c = MQTTClient("umqtt_client", server)
    c.set_callback(sub_cb)
    c.connect()
    print("Subscribing to: ", topic)
    c.subscribe(topic)

    lastMsgTime = msgTime
    
    while True:
        # Set to True/False depending on whether you want to test
        # blocking I/O or not. NOTE: Setting to True makes it
        # difficult to Control-C when using WebREPL.
        if False:
            # Blocking wait for message
            print("Waiting for new message from topic: ", topic)
            c.wait_msg()
        else:
            # Non-blocking wait for message
            print("Checking for new message from topic: ", topic)
            c.check_msg()

        mtime = msgTime
        msg = msgRxd
        if mtime != lastMsgTime and msgRxd != None:
            print((topic, msg))
            lastMsgTime = mtime
            msgCnt = msgCnt + 1
            updateLedState(connectOut, msgCnt)
        else:
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep_ms(1000)

    c.disconnect()

if __name__ == "__main__":
    main()
