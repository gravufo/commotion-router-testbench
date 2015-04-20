#!/usr/bin/python
import sys
import flash
import getopt
import routingTest.testRouting

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:","ifile=")
    except getopt.GetoptError:
        print 'commotion-router-testbench.py -i <inputfile>'
        sys.exit(2)

    if(len(opts) == 0):
         print 'commotion-router-testbench.py -i <inputfile>'
         sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'commotion-router-testbench.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFile = arg

    ## We will not move the files (try to do it through jenkins or something?)

    # Copy new build to the tftp server (overwrite older builds)
    # openwrt-ar71xx-generic-hornet-ub-x2-kernel.bin
    #os.system("cp " + kernelPath + " " + tftpPath + "kernel.bin")
    # openwrt-ar71xx-generic-hornet-ub-x2-rootfs-squashfs.bin
    #os.system("cp " + rootfsPath + " " + tftpPath + "rootfs.bin")

    # Read from input file the serial ports (routers) to communicate with
    file = open(inputFile, 'r')

    counter = 1
    routerNumber = 1
    routersToTest = []

    for line in file:

        line = line.rstrip('\n')

        if line.startswith("/dev/tty"):
            # Flash new build on routers
            ipaddr = "192.168.2.1%d" % counter

            counter += 1

            if flash.flash(line, ipaddr):
                routerNumber += 1
                routersToTest.append(line)
            else:
                # For now, if a flash fails, you will need to reboot that router into uboot manually and run the script
                # on that router again (or flash manually if you prefer).
                print("Flashing failed on router with port " + line)

    # Ping test each router to make sure mesh is up



if __name__ == "__main__":
   main(sys.argv[1:])
   quit()