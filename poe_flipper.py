from fabric import Connection
from fabric import SerialGroup as Group
import time
import sys, getopt


def kill_poe(
    flip_info,
):  ## if we kill without planning on restoring in same run, will need to write IPs and interfaces to a file
    c = flip_info[0]
    dryrun = flip_info[2]
    interfaces = flip_info[3]
    print("killing POE to interfaces: " + interfaces + " on " + c.host)

    if dryrun is False:
        poe_off_result = c.run("configure\n interface " + interfaces + "\n no link-poe")


def restore_poe(flip_info):
    c = flip_info[0]
    dryrun = flip_info[2]
    interfaces = flip_info[3]
    print("restoring POE")

    if dryrun is False:
        poe_on_result = c.run("configure\n interface " + interfaces + "\n link-poe")


def flip_poe(flip_info):
    c = flip_info[0]
    dryrun = flip_info[2]
    kill_poe(flip_info)

    if dryrun is False:
        print("killed, sleeping for 5 seconds.....")
        time.sleep(5)
    else:
        print("if not dry run, would sleep for 5 seconds")

    restore_poe(flip_info)


def connect_to_switch(flip_info):
    c = flip_info[0]
    mac_address_prefix = flip_info[1]

    print("connecting to " + c.host + ", looking for prefix " + mac_address_prefix)
    ## connect to switch and get the mac-address-table of the prefix we're interested in
    ## really only need to exclude 1/1/48 for Etech Switch because it's using a copper uplink
    ### should probably work some logic in around that...
    kwargs = {
        "timeout": 5,
        "hide": True,
    }  ## should probably add this variable to flip_info and have hide be a verbose command switch
    try:
        result = c.run(
            "show mac-address-table | exclude lag1 | include " + mac_address_prefix,
            **kwargs
        )
    except:
        print(
            "an error occured while atempting to grab the mac address table of "
            + c.host
        )
        sys.exit(2)

    mac_address_table = result.stdout.split()
    if len(mac_address_table) == 0:
        sys.exit(
            "no interfaces with mac_prefix "
            + mac_address_prefix
            + " found at "
            + c.host
        )

    mac_address_table.insert(
        0, "placeholder"
    )  # add a placeholder so modulo math below is easier

    ## take mac_address_table and assign the interface numbers to interface variable
    ## interface number is every 4th table entry, thanks to our placeholder
    for i in range(len(mac_address_table)):
        if i % 4 == 0 and i != 0:
            if i == 4:
                interfaces = mac_address_table[i]
            else:
                interfaces = interfaces + "," + mac_address_table[i]

    ## check those interface to see if any are trunk ports
    result = c.run("show interface " + interfaces + " brief | in trunk", **kwargs)
    result = result.stdout.split()
    result_len = len(result)

    if result_len > 1 and result_len < 12:
        trunk_port = result[0]
        trunk_port = trunk_port + ","

        print("single trunk port on " + trunk_port + " removing from interface list")

        while interfaces.find(trunk_port) != -1:
            interfaces = interfaces.replace((trunk_port), "")

        trunk_port = trunk_port.rstrip(trunk_port[-1])  ## remove trailing comma

        while (
            interfaces.find(trunk_port) != -1
        ):  ## grab that last interface without a comma if needed
            interfaces = interfaces.replace(trunk_port, "")

        if len(interfaces) == 0:
            print("that was all the interfaces...")
            sys.exit()

    elif result_len > 12:
        print("multiple trunk ports. not handled yet")
        sys.exit(2)

    flip_info.insert(3, interfaces)

    return flip_info


def main(argv):
    ## arg parsing
    try:
        opts, args = getopt.getopt(
            argv,
            "hm:t:v:f:s:dk:",
            [
                "help",
                "mac-prefix=",
                "device-type=",
                "venue=",
                "switch-ip=",
                "dryrun",
                "keyfile",
            ],
        )
    except getopt.GetoptError:
        print("poe_flipper.py -m 00:02 -s 172.25.1.37")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("poe_flipper.sh -m <mac-prefix> -s <switch-ip> or -f <host-file>")
            sys.exit()
        elif opt in ("-m", "--mac-prefix"):
            mac_address_prefix = arg
        elif opt in (
            "-t",
            "--device-type",
        ):  ## add other device types and their mac address prefixes here
            if arg == "eztv":
                mac_address_prefix = "00:02:02"
            elif arg == "dante":
                mac_address_prefix = "00:1d:c1"
            elif arg == "crestron":
                mac_address_prefix = "00:10:7f"
        elif opt in ("-v", "--venue"):
            venue = arg
        elif opt in (
            "-s",
            "--switch-ip",
        ):  # as of now, we only support a single IP address at a time
            switchIP = []
            switchIP.append(
                arg
            )  ## default behavior is for switchIP to be a list that's unpacked below. Even though this is a single IP, we have to make it a list
        elif opt in (
            "-d",
            "--dryrun",
        ):  ## prevents the actual POE commands from being sent, but does grab interfaces
            dryrun = True
        elif opt in ("-k", "--keyfile"):  ## location of keyfile
            keyLocation = arg

    ## some error handling. should probably do some string verification here as well
    if "mac_address_prefix" not in locals():
        print("need to assign a mac-address-prefix with -m or device type with -t")
        sys.exit(2)

    elif ("switchIP" not in locals()) and ("venue" not in locals()):
        print("a switch IP address via -s or venue via -v is required")

    if "dryrun" not in locals():
        dryrun = False

    if "keyLocation" not in locals():
        keyLocation = "/home/tyler/.ssh/ida_rsa-copy"

    if "venue" in locals():
        if (
            venue == "BDS"
        ):  ## should probably seperate these into another file, either in hostfile format or json
            ## somehow admin shutdown the 1/1/16 interface on switch 172.25.1.50 that feeds etech office. removed that switch ip for now
            ## likely has to do with how etech office is fed
            switchIP = [
#                "172.25.1.23",
#                "172.25.1.24",
#                "172.25.1.25",
#                "172.25.1.26",
#                "172.25.1.27",
#                "172.25.1.28",
#                "172.25.1.29",
#                "172.25.1.30",
#                "172.25.1.31",
#                "172.25.1.32",
#                "172.25.1.33",
#                "172.25.1.34",
#                "172.25.1.35",
#                "172.25.1.36",
#                "172.25.1.37",
                "172.25.1.38",
                "172.25.1.39",
                "172.25.1.40",
                "172.25.1.41",
                "172.25.1.42",
                "172.25.1.43",
                "172.25.1.44",
                "172.25.1.45",
                "172.25.1.46",
                "172.25.1.47",
                "172.25.1.48",
                "172.25.1.49",
                "172.25.1.50",
                "172.25.1.51",
                "172.25.1.52",
                "172.25.1.60",
                "172.25.1.67",
            ]

    for connection in Group(
        *switchIP,
        user="scripts",
        connect_timeout=3,
        connect_kwargs={
            "key_filename": [
                keyLocation,
            ],
            "auth_timeout": 5,
        }
    ):
        flip_info = [connection, mac_address_prefix, dryrun]
        try:
            flip_info = connect_to_switch(flip_info)
        except:  ## should figure out how to quiet errors. also how to raise different exceptions
            print("an error occurred connecting to " + connection.host)
        else:
            if dryrun is True:
                print("Executing Dry Run now!!")

            flip_poe(flip_info)

        ## a few blank lines to break things up
        print()
        print()
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
