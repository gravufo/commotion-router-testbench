#!/usr/bin/python
import os

######################################################################################
# Function: ping()
# Description: This function sends 2 packets to a host and checks the availability
# Parameter: hostname or address
# Return: 0 if host is alive or anything else if not
######################################################################################
def ping(hostname):
    return os.system("ping" + " " + hostname + " -c 2" + " > /dev/null")


######################################################################################
# Function: aliveHost()
# Description:Check all host who are aline in a giving pool
# Parameter: pool (ipStart of pool and ipEnd of pool)
# Return: A string vector of all alive hosts
######################################################################################      
def aliveHost(ipStart, ipEnd):
    aliveHost = []
    while ipStart != "End" and ipStart != "Error!":
        if ipStart != "End":
            if not (ping(ipStart)):
                aliveHost.append(ipStart)
        ipStart = nextIpInPool(ipStart, ipEnd)
    return aliveHost


######################################################################################
# Function: existHost()
# Description:Check if a giving host exist in a network pool 
# Parameter: pool, host
# Return: 1 if exist or 0 if not
######################################################################################
def existHost(pool, host):
    exist = 0
    poolSize = len(pool)
    while poolSize >= 0:
        if pool[poolSize - 1] == host:
            exist = 1
            break
        poolSize = poolSize - 1
    return exist


######################################################################################
# Function: hostsUndone()
# Description: return hosts who are alive and not again done
# Parameter: Last done Hosts and the new giving hosts
# Return: 
######################################################################################
def hostsUnDone(lastDoneHosts, NewHostsToCheck):
    unDone = []
    nbrHosts = len(NewHostsToCheck)
    while nbrHosts > 0:
        nbrHosts = nbrHosts - 1
        host = NewHostsToCheck[nbrHosts]
        if not (existHost(lastDoneHosts, host)):
            unDone.append(host)
    return unDone


######################################################################################
# Function:nextIpInPool()
# Description:give the next ip who follow a giving ip
# Parameter: ipStart, ipEnd
# Return: String who represent the next ip 
######################################################################################
def nextIpInPool(ipStart, ipEnd):
    nxtIp = "Error!"

    net11 = int(ipStart.split(".")[0])
    net12 = int(ipStart.split(".")[1])
    net13 = int(ipStart.split(".")[2])
    net14 = int(ipStart.split(".")[3])

    net21 = int(ipEnd.split(".")[0])
    net22 = int(ipEnd.split(".")[1])
    net23 = int(ipEnd.split(".")[2])
    net24 = int(ipEnd.split(".")[3])

    net11net21 = net21 - net11
    net12net22 = net22 - net12
    net13net23 = net23 - net13
    net14net24 = net24 - net14

    if net11net21 != 0:  #
        if net14 != 255:  # . . . xxx
            firstHost = int(ipStart.split(".")[3])
            nxtIp = str(net11) + "." + str(net12) + "." + str(net13) + "." + str(firstHost + 1)
        elif net13 != 255:  # . .xxx.
            net14 = 0
            firstHost = int(ipStart.split(".")[2])
            nxtIp = str(net11) + "." + str(net12) + "." + str(firstHost + 1) + "." + str(net14)
        elif net12 != 255:  # . .xxx.
            net13 = 0
            firstHost = int(ipStart.split(".")[1])
            nxtIp = str(net11) + "." + str(firstHost + 1) + "." + str(net13) + "." + str(net14)
        elif net11 != 255:
            net12 = 0
            firstHost = int(ipStart.split(".")[0])
            nxtIp = str(firstHost + 1) + "." + str(net12) + "." + str(net13) + "." + str(net14)

    elif net12net22 != 0:  # xxx. .xxx.xxx
        if net14 != 255:  # . . . xxx
            firstHost = int(ipStart.split(".")[3])
            nxtIp = str(net11) + "." + str(net12) + "." + str(net13) + "." + str(firstHost + 1)
        elif net13 != 255:  # . .xxx.
            net14 = 0
            firstHost = int(ipStart.split(".")[2])
            nxtIp = str(net11) + "." + str(net12) + "." + str(firstHost + 1) + "." + str(net14)
        elif net12 != 255:  # . .xxx.
            net13 = 0
            firstHost = int(ipStart.split(".")[1])
            nxtIp = str(net11) + "." + str(firstHost + 1) + "." + str(net13) + "." + str(net14)

    elif net13net23 != 0:  # xxx.xxx. .xxx
        if net14 != 255:  # . . . xxx
            firstHost = int(ipStart.split(".")[3])
            nxtIp = str(net11) + "." + str(net12) + "." + str(net13) + "." + str(firstHost + 1)
        else:  # . .xxx.
            net14 = 0
            firstHost = int(ipStart.split(".")[2])
            nxtIp = str(net11) + "." + str(net12) + "." + str(firstHost + 1) + "." + str(net14)

    elif net14net24 != 0:  # xxx.xxx.xxx.
        firstHost = int(ipStart.split(".")[3])
        if firstHost <= 254:
            nxtIp = str(net11) + "." + str(net12) + "." + str(net13) + "." + str(firstHost + 1)
    else:
        nxtIp = "End"
    return nxtIp
