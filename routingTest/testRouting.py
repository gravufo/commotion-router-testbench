from toolsRouting import *

########################################################
# Main test
########################################################


def test(ports):
    # get ip of routers ports
    ipsRouters = []

    for port in ports:
        ip_address = getIpRouterMesh(port, 115200)
        ipsRouters.append(ip_address)

    # Create arrayList of IP, port, rate
    arrayList = []
    for ip in ipsRouters:
        if ip != "":
            arrayList.append(ip, ports[int(i)], rates[int(i)])

    # Test the connectivity of router in the Mesh
    arrayListLogPing = getMeshRoutingStatistic(arrayList)

    # Write result on a file
    writeFile("log.txt", arrayListLogPing)