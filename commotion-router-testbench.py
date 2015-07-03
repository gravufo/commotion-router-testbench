import flash
import argparse


def test_firmware_image(router_list_file):
    ## We will not move the files (try to do it through jenkins or something?)

    # Copy new build to the tftp server (overwrite older builds)
    # openwrt-ar71xx-generic-hornet-ub-x2-kernel.bin
    # os.system("cp " + kernelPath + " " + tftpPath + "kernel.bin")
    # openwrt-ar71xx-generic-hornet-ub-x2-rootfs-squashfs.bin
    # os.system("cp " + rootfsPath + " " + tftpPath + "rootfs.bin")
    routers = []

    # Read from input file the serial ports (routers) to communicate with
    with open(router_list_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')

            if line.startswith('/dev/tty'):
                # Flash new build on routers
                routers.append(line)

    for i, r in enumerate(routers):
        ip = '192.168.2.1{0}'.format(i)

        if flash.flash(r, ip):
            routers.append(r)
        else:
            # For now, if a flash fails, you will need to reboot that router into uboot manually and run the script
            # on that router again (or flash manually if you prefer).
            print("Flashing failed on router with port " + r)

            # Ping test each router to make sure mesh is up


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Validate the Commotion Wireless firmware using real devices connected to their serial console port.')

    parser.add_argument('routers_list_file',
                        help='File containing the serial port used to control the routers used by the testbench. '
                             '(One port per router each on it\'s own line)')
    args = parser.parse_args()

    test_firmware_image(args.routers_list_file)
    quit()
