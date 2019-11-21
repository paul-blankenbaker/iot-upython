import json
import socket
import uselect
import time

def runServer():
    keepRunning = True
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    webSocket = socket.socket()
    webSocket.bind(addr)
    webSocket.listen(1)
    
    while keepRunning:
        cl = None

        try:
            cl, addr = webSocket.accept()
            # Setting timeout is important to clean up poorly behaved
            # client connections
            cl.settimeout(0.0)

            # Wait until some data is available, then wait a bit more
            poller = uselect.poll()
            poller.register(cl, uselect.POLLIN)
            for i in range(1,20):
                # time in milliseconds
                res = poller.poll(50)
                if res:
                    break
            poller.unregister(cl)
            time.sleep(0.010)

            # Read in data that is available (up to 8K - might be issue if browser
            # sends a ton of crud in the header)
            data = cl.read(8192)
            if data:
                lines = data.split(b"\r\n")
            else:
                lines = []

            jsonStr = None
            fileResp = None
            needPostData = False
            nextIsPostData = False
            
            for line in lines:
                #line = cl_file.readline()
                #print(line)
                if line.find(b'GET') != -1:
                    if line.find(b'GET /wificonfig.json') != -1:
                        fileResp = "wificonfig.json"
                        mimeType = b"application/json"
                    elif line.find(b'GET /wificonfig.html') != -1 or line.find(b'GET / ') != -1:
                        fileResp = "wificonfig.html"
                        mimeType = b"text/html"
                    break
                elif line.find(b'POST /wificonfig.json') != -1:
                    needPostData = True
                elif needPostData and (len(line) == 0):
                    nextIsPostData = True
                elif nextIsPostData:
                    jsonStr = line.decode()
                    break

            needReset = False

            if jsonStr != None:
                cfg = json.loads(jsonStr)
                with open('wificonfig.json', 'w') as outFile:
                    json.dump(cfg, outFile)
                fileResp = "wificonfig.json"
                mimeType = b"application/json"
                needReset = True
                #print("Updated config JSON with:", jsonStr)
    
            if fileResp != None:
                #print("Attempting to read:", fileResp)
                f = open(fileResp)
                response = f.read()
                f.close()
                #print("Attempting to send back:", fileResp)
                data = response.encode()
                totallen = len(data)
                header = b"HTTP/1.1 200 OK\r\nContentType: " + mimeType + b"\r\nContent-Length: " + str(totallen).encode() + b"\r\nConnection: close\r\n\r\n"
                cl.send(header)
                totalsent = 0
                while totalsent < totallen:
                    sent = cl.send(data[totalsent:])
                    totalsent = totalsent + sent
                    #print("Sent:", totalsent, " of:", totallen)
            else:
                header = b"HTTP/1.1 404 Not Found\r\nContentType: text/plain\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                cl.send(header)
            cl.close()

            if needReset:
                #print("Resetting ESP32 to load new settings")
                time.sleep(0.05)
                import machine
                machine.reset()
                        
        except KeyboardInterrupt:
            keepRunning = False
            if (cl != None):
                h = cl
                cl = None
                h.close()
        except Exception as err:
            #print("Exception occurred, closing current connection", err)
            # Be paranoid about closing out connections to prevent
            # open file and/or memory leaks!
            if (cl != None):
                h = cl
                cl = None
                try:
                    h.close()
                except Exception as err:
                    pass
                    #print("Exception occurred, when closing connection", err)
    
    webSocket.close()
