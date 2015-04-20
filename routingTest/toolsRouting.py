import serial
import pexpect
import fdpexpect
import time
import fcntl

######################################################################################
# Function: getIpRouterMesh()
# Description: This function return the Ip router of giving router
# Parameter: serial port name and  rate the baudrate
# Return: The IP of the router or  error
######################################################################################
def getIpRouterMesh(port, baudrate):
    IpRouter = ""
    try:
        ser = serial.Serial(port, baudrate)
    except IOError:
        return IpRouter

    if ser.isOpen():
        reader = fdpexpect.fdspawn(ser, 'wb', timeout=90)
        reader.send("\x03")
        reader.send("ifconfig\x0D")
        try:
            reader.expect("br-lan")
            reader.expect("inet addr:")
            contentLine = reader.readline()
            ipFound = contentLine.split("Bcast", 1)[0]
            ipFound = ipFound.replace(" ", "")
            IpRouter = ipFound
            # regex = re.compile(r"\d+.\d+.\d+.\d+")  #Ne marcche pas en attendant j ai remplace par un split
            #print ("VALEUR DE REGEX  ="),regex
            #ipFound = regex.match(contentLine)
            #listMeshIP.append(ipFound) # Add IP
        except pexpect.TIMEOUT:
            success = False
        except pexpect.EOF:
            print("Unexpected EOF reached. Aborting.")
            return False
        reader.close()
    # ser.close() # close port
    else:
        print("Serial port not open" + ser.name)
    return IpRouter


######################################################################################
# Function: testMeshRouting()
# Description: This function test the connectivity of giving ip router together
# Parameter: a three dimension array ( ip, port, rate )
# Return: A list with all ip with connectivity status
######################################################################################
def getMeshRoutingStatistic(ArrayIpsAndSerialPort):
    statistic = []
    # loop on Array IPs Mesh and ping it together
    for i in range(len(ArrayIpsAndSerialPort) - 1):
        compteur = i

        currentIpRouter = ArrayIpsAndSerialPort[compteur][0]
        currentSerialPortRouter = ArrayIpsAndSerialPort[compteur][1]
        currentBaudrate = ArrayIpsAndSerialPort[compteur][2]
        try:
            ser = serial.Serial(currentSerialPortRouter,
                                currentBaudrate)  # open current router serial port
        except IOError:
            continue
        if ser.isOpen():
            try:
                fcntl.flock(ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                reader = fdpexpect.fdspawn(ser)
            except IOError:
                print 'Port {0} is already in use.'.format(ser.name)
                return False
        reader.send("\x03")

        # loop on all ip and ping routers together
        while compteur < len(ArrayIpsAndSerialPort) - 1:

            compteur = compteur + 1

            # Get Next ip on the IpArraylist
            nextIpRouter = ArrayIpsAndSerialPort[compteur][0]

            # send ping to ping neighbordRouter
            time.sleep(1)
            pingNextRouter = "ping " + nextIpRouter + " -c 4\x0D"
            reader.send(pingNextRouter)

            try:
                totalPacketsReceived = 0
                reader.expect("packets transmitted,")
                contentLine = reader.readline()
                totalPacketsReceived = contentLine.split("packets", 1)[0]
                totalPacketsReceived = int(totalPacketsReceived.replace(" ", ""))
                #####################################################
                # With regular expression does work!!!
                # regex = re.compile(r"\s\d+\spackets received,")
                #result = regex.match(contentLine)
                #if result is not None:
                #try:
                #totalReceive = int(result.group(1))
                #except:
                #print("Catastroph!!")
                #####################################################
                #print ("TOTAL RECEIVED = "),totalPacketsReceived
                if totalPacketsReceived >= 2:  # Total send Packet is 4 we assume that router is alive
                    print("Ping: " + currentIpRouter + " ---> " + nextIpRouter + " : ok!")
                    statistic.append([currentIpRouter, nextIpRouter, "Success"])
                else:
                    print("Ping: " + currentIpRouter + " ---> " + nextIpRouter + " : Fail!")
                    statistic.append([currentIpRouter, nextIpRouter, "Fail"])

            except pexpect.TIMEOUT:
                return False
            except pexpect.EOF:
                return False

        reader.close()
    return statistic


######################################################################################
# Function: writeFile()
# Description: This function create a file an write on it with giving parameter
# Parameter: Name file:fileName, content:arrayListLogPing
# Return: None or False if error
######################################################################################
def writeFile(fileName, arrayListLogPing):
    try:
        f = open(fileName, 'w')
        for i in range(len(arrayListLogPing)):
            f.writelines(str(arrayListLogPing[int(i)]) + "\n")
        f.close()

    except:
        return False 