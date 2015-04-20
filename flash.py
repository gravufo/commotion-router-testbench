import serial
import pexpect
import fdpexpect
import re
import os
import time
import fcntl


def flash(serialPort, ipaddr):
    try:
        ser = serial.Serial(serialPort,115200)  # open the serial port
        print (ser.name)          # check which port was really used
    except serial.serialutil.SerialException as ex:
        print 'Port {0} is unavailable: {1}'.format(serialPort, ex)
        return False

    if ser.isOpen():
        try:
            fcntl.flock(ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            reader = fdpexpect.fdspawn(ser)#, 'wb', timeout=50)
        except IOError:
            print 'Port {0} is already in use.'.format(ser.name)
            return False

    print("Waiting for Command Prompt")

    success = False

    while not success:
        try:
            reader.send("\x03")
            state = reader.expect(["#", "Please press Enter to activate this console.", "ar7240>"])

            if state == 0 or state == 1:
                print("Activating Commotion console")
                reader.send("\x0D")
                reader.expect("#")
                print("Sending reboot command")
                reader.sendline("reboot")
                reader.expect("Hit any key to stop autoboot")
                time.sleep(1)
                reader.send("F")
                print("Waiting for uboot Command Prompt")
                reader.expect("ar7240>")
            else:
                success = True
        except pexpect.TIMEOUT:
            success = False
        except pexpect.EOF:
            print("Unexpected EOF reached. Aborting.")
            reader.close()             # close port
            return False

    # Set the correct IP Address
    reader.send("setenv ipaddr " + ipaddr + "\x0D")
    reader.expect("ar7240>")
    reader.send("setenv serverip 192.168.2.100\x0D")
    reader.expect("ar7240>")

    time.sleep(4)

    ########################################################
    # Flash the kernel
    ########################################################

    actualSize = int(hex(os.path.getsize("/srv/tftp/kernel.bin")).lstrip('0x'))
    receivedSize = -1

    print("Downloading new kernel")

    while receivedSize != actualSize:
        reader.send("tftp 0x80600000 kernel.bin\x0D")
        reader.expect("done\r\n")
        receivedSizeLine = reader.readline()
        reader.expect("ar7240>")

        # Bytes\stransferred\s=\s\d+\s\((\d+)\shex\)
        regex = re.compile(r"Bytes\stransferred\s=\s\d+\s\((\d+)\shex\)")
        result = regex.match(receivedSizeLine)
        if result is not None:
            try:
                receivedSize = int(result.group(1))
            except:
                print("Something went terribly wrong")
                receivedSize = 0

        print("Verifying file integrity...")
        print("Received size %d hex" % receivedSize)
        print("Actual size %d hex" % actualSize)
        if receivedSize != actualSize:
            print("Does not match, restarting download...")
        else:
            print("Match, starting flash")

    # Erase the kernel partition
    print("Erasing old kernel")
    reader.send("erase 0x9fe50000 +0x190000\x0D")
    reader.expect("Erased 25 sectors")
    reader.expect("ar7240>")

    # Copy the new kernel to the now empty partition
    print("Copying new kernel")
    command = "cp.b 0x80600000 0x9fe50000 %d\x0D" % receivedSize
    reader.send(command)
    reader.expect("done")
    reader.expect("ar7240>")


    ########################################################
    # Flash the rootfs
    ########################################################

    actualSize = int(hex(os.path.getsize("/srv/tftp/rootfs.bin")).lstrip('0x'))
    receivedSize = -1

    print("Downloading new rootfs")

    while receivedSize != actualSize:
        reader.send("tftp 0x80600000 rootfs.bin\x0D")
        reader.expect("done\r\n", timeout=60)
        receivedSizeLine = reader.readline()
        reader.expect("ar7240>")

        # Bytes\stransferred\s=\s\d+\s\((\d+)\shex\)
        regex = re.compile(r"Bytes\stransferred\s=\s\d+\s\((\d+)\shex\)")
        result = regex.match(receivedSizeLine)
        if result is not None:
            try:
                receivedSize = int(result.group(1))
            except:
                print("Something went terribly wrong")
                receivedSize = 0

        print("Verifying file integrity...")
        print("Received size %d hex" % receivedSize)
        print("Actual size %d hex" % actualSize)
        if receivedSize != actualSize:
            print("Does not match, restarting download...")
        else:
            print("Match, starting flash")

    # Erase the rootfs partition
    print("Erasing old rootfs")
    reader.send("erase 0x9f050000 +0xe00000\x0D")
    reader.expect("Erased 224 sectors", timeout=90)
    reader.expect("ar7240>")

    # Copy the new rootfs to the now empty partition
    print("Copying new rootfs")
    command = "cp.b 0x80600000 0x9f050000 %d\x0D" % receivedSize
    reader.send(command)
    reader.expect("done")
    reader.expect("ar7240>")

    try:
        print("Booting into freshly flashed firmware!")
        reader.send("boot\x0D")
        reader.expect("Please press Enter to activate this console.")
        print("Done!")
    except pexpect.TIMEOUT:
        reader.close()             # close port
        return False
    except pexpect.EOF:
        print("Unexpected EOF reached. Aborting.")
        reader.close()             # close port
        return False

    configure(reader, 2)

    reader.close()             # close port

    return True


def configure(reader, routerNumber):

    reader.send("\x0D")
    reader.expect("#")

    # Deactivate console logging, because it breaks everything
    reader.send("dmesg -n 1\x0D")
    reader.expect("#")

    time.sleep(60)

    print("Changing root password")
    reader.send("passwd\x0D")
    reader.expect("New password:")
    reader.send("qwerty\x0D")
    reader.expect("Retype password:")
    reader.send("qwerty\x0D")
    reader.expect("#")

    ######################################################################
    #
    #   WARNING: The two following lines are a temporary workaround to a
    #           bug that was found with setupwizard CLI. Remove when fix
    #           is integrated in Commotion
    #
    ######################################################################
    reader.send("chmod +x /usr/bin/setupwizard\x0D")
    reader.expect("#")

    print("Running setup wizard")
    reader.send("setupwizard\x0D")

    print("Setting hostname")
    reader.expect("[y/n]")
    reader.send("y\x0D")

    reader.expect("hostname:")
    reader.send("Node%d\x0D" % routerNumber)

    print("Configuring radio")
    reader.expect("[y/n]")
    reader.send("y\x0D")

    reader.expect("radio0:")
    reader.send("commotion\x0D")

    reader.expect("channel:")
    reader.send("11\x0D")

    reader.expect("[y/n]")
    reader.send("n\x0D")

    reader.expect("[y/n]")
    reader.send("y\x0D")

    reader.expect("name:")
    reader.send("Node%d\x0D" % routerNumber)

    reader.expect("[y/n]")
    reader.send("n\x0D")

    print("Saving configuration")
    reader.expect("[y/n]")
    reader.send("y\x0D")

    ######################################################################
    #
    #   WARNING: The two following lines are a temporary workaround to a
    #           bug that was found with setupwizard CLI. Remove when fix
    #           is integrated in Commotion
    #
    ######################################################################
    reader.send("/etc/init.d/firewall stop\x0D")
    reader.expect("#")
