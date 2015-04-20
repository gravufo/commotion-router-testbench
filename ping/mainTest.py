from netools import nextIpInPool, ping, aliveHost, hostsUnDone


def main():
    aliveHosts = []
    # pool IP
    ipStart = "192.168.56.1"
    ipEnd = "192.168.56.5"

    print"Pools: ", ipStart + " -> " + ipEnd

    print"Scanning online Router on network..."
    aliveHosts = aliveHost(ipStart, ipEnd)

    print "online Router:"
    print aliveHosts

# print"New Hosts Alive in Pools:",hostsUnDone(aliveHosts, aliveHost(ipStart,ipEnd))

if __name__ == '__main__':
    main()
