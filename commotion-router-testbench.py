#!/usr/bin/python
import sys
import flash
import getopt
import routingTest.testRouting


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:", "ifile=")
    except getopt.GetoptError:
        print 'commotion-router-testbench.py -i <inputfile>'
        sys.exit(2)

    if len(opts) == 0:
        print 'commotion-router-testbench.py -i <inputfile>'
        sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'commotion-router-testbench.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg

    ## We will not move the files (try to do it through jenkins or something?)

    # Copy new build to the tftp server (overwrite older builds)
    # openwrt-ar71xx-generic-hornet-ub-x2-kernel.bin
    # os.system("cp " + kernelPath + " " + tftpPath + "kernel.bin")
    # openwrt-ar71xx-generic-hornet-ub-x2-rootfs-squashfs.bin
    # os.system("cp " + rootfsPath + " " + tftpPath + "rootfs.bin")
    routers = []

    # Read from input file the serial ports (routers) to communicate with
    with open(input_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')

            if line.startswith('/dev/tty'):
                # Flash new build on routers
                routers.append(line)

    for i, r in enumerate(routers):
        ip = '192.168.2.1{0}'.format(i)

        if flash.flash(r, ip):
            routers.append(line)
        else:
            # For now, if a flash fails, you will need to reboot that router into uboot manually and run the script
            # on that router again (or flash manually if you prefer).
            print("Flashing failed on router with port " + r)

            # Ping test each router to make sure mesh is up


if __name__ == "__main__":
    main(sys.argv[1:])
    quit()
