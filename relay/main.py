# Simple Web interface that provides button in web page
# that user can click on to open a garage door (requires
# wiring I/O pin to a relay and connecting the relay
# in parallel with your garage door switch)
import machine
import socket
import time
import utime

# BEGIN CONFIGURATION SECTION (YOU MAY NEED TO ADJUST THESE VALUES)

# What output pin on your board is tied to the relay
# doorPin = 33 # On ESP32 board
doorPin = 5

# Logical value to set on pin in order to "press" the garage door button
buttonPressed = False

# Number of seconds to hold button in "pressed" state
buttonPressTime = 0.1

# Set to True for debugging output in REPL
debug = False

# Set to False to disable automatic start of web server
autoStart = True

# END OF CONFIGURATION SECTION

# Output pin on that drives relay controlling the garage door
buttonReleased = not buttonPressed
door = machine.Pin(doorPin, machine.Pin.OUT, value=buttonReleased)

# Helper function to "press" the garage door button for a fraction
# of a second
def toggleDoor():
    global door
    global buttonPressed
    global buttonReleased
    global buttonPressTime
    door.value(buttonPressed)
    time.sleep(buttonPressTime)
    door.value(buttonReleased)

# HTTPD Header to send back (NOTE: Safari
# really wants to see HTTP/1.1 in the response
# header otherwise it will disable JavaScript
# and the button won't be usable)
httpdHeaderCommon = "HTTP/1.1 200 OK\r\n"
httpdHeaderHtml = "Content-Type: text/html\r\n\r\n"

# HTML document to send back to clients
html = httpdHeaderCommon + httpdHeaderHtml + """<!DOCTYPE html>
<html>
  <head>
    <title>Garage Door</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <script>
// Helper functions to handle button press using XMLHttpRequest() to prevent
// inclusion of "open=true" in URL used to open the door (so if user
// presses reload after opening the door it won't open again)
function buttonPressed(event) {
  location.reload();
}

function pressButton() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/garage/open=true');
  // Reload page when submission is acknowledged
  xhr.addEventListener('load', buttonPressed);
  xhr.send();
}
    </script>
  </head>
  <body>
    <div style="text-align: center; margin-top: 100px;">
      <button style="font-size: 32pt;" onclick="pressButton();">Garage Door</button>
    </div>
    <div style="text-align: center; font-size: 8pt; margin-top: 4px;">Views: %d  Presses: %d  Ignored: %d</div>
  </body>
</html>
"""

# 404 document for bad requests
err404 = """HTTP/1.1 404 Not Found
ContentType: text/plain

404 - The requested URL was not found
"""

# Opens port 80 on the IOT device in listen mode and starts
# listening for incoming connections.
def openListener(webSocket):
    if webSocket != None:
        return webSocket
    # on port 80
    if debug:
        print('Opening up socket listener on port 80')
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    webSocket = socket.socket()
    webSocket.bind(addr)
    webSocket.listen(1)
    if debug:
        print('Opened server socket, listening on: ', addr)
    return webSocket

# Main body of application that processes incoming requests
# from web browsers. Handles following URLs:
#
#   http://192.168.4.1/garage - Renders HTML page
#   http://192.168.4.1/garage?open=true - Renders HTML page AND presses garage door button
#   Everything else gets a 404 back.
#
# NOTE: If you connect your IOT device to your local LAN, you can
# substitute the IP address on the local LAN for 192.168.4.1 (avoids
# having to switch to the IOT WIFI AP).
def runServer():
    # Keep track of door open requests, page requests and invalid page requests
    toggleCnt = 0
    viewCnt = 0
    attackCnt = 0
    keepRunning = True
    webSocket = openListener(None)
    acceptTime = 0
    reqTime = 0
    respTime = 0
    buttonTime = 0
    
    while keepRunning:
        needToOpen = False
        needToShow = False
        cl = None

        try:
            cl, addr = webSocket.accept()
            if debug:
                acceptTime = utime.ticks_ms();
                print('client connected from ', addr)

            # Setting timeout is important to clean up poorly behaved
            # client connections
            cl.settimeout(1.0)
            cl_file = cl.makefile('rwb', 0)
        
            while True:
                line = cl_file.readline()
                if not line or line == b'\r\n':
                    break
                if debug:
                    print(line);
                if line.find(b'GET /garage') != -1:
                    needToShow = True
                    if line.find(b'open=true') != -1:
                        needToOpen = True

            reqTime = utime.ticks_ms()
            
            if needToShow:
                if needToOpen:
                    toggleCnt = toggleCnt + 1
                
                viewCnt = viewCnt + 1
                response = html % (viewCnt, toggleCnt, attackCnt)
                cl.send(response)
            else:
                needToOpen = False
                attackCnt = attackCnt + 1
                if debug:
                    print("WARNING - ignored request from client");
                cl.send(err404)

            h = cl;
            cl = None
            h.close()
            respTime = utime.ticks_ms()

            # Defer pressing of button until after we sent back a response
            if needToOpen:
                toggleDoor()
                if debug:
                    toggleTime = utime.ticks_ms() - respTime
                    print("Garage door button press number %d took %d ms" % (toggleCnt, toggleTime))

            if debug:
                print("Request came in %d ms, Response sent in %d ms" % (reqTime - acceptTime, respTime - reqTime))
                        
        except KeyboardInterrupt:
            keepRunning = False
            if (cl != None):
                h = cl
                cl = None
                h.close()
        except Exception as err:
            time.sleep(0.1)
            if debug:
                print("Exception occurred, closing current connection", err)
            # Be paranoid about closing out connections to prevent
            # open file and/or memory leaks!
            if (cl != None):
                h = cl
                cl = None
                try:
                    h.close()
                except Exception as err:
                    print("Exception occurred, when closing connection", err)


# Start up web server (unless automatic start has been disabled)
if autoStart:
    runServer()
