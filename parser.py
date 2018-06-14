#!/usr/bin/env python

import sys
import re

try:

    #Open File for reading:
    switch_config_file = open(sys.argv[1], 'r')
    switch_config = switch_config_file.read()

    #STEP 1
    #Look for infrastructure_port information

    #search for the first
    current_search_pattern = "show cdp nei | e SEP"
    index_a = switch_config.find(current_search_pattern)

    if index_a == -1:
        print("Error: Could not locate Infrastructure port Information, exiting.")
        exit()

    current_search_pattern = "Total cdp entries displayed :"
    index_b = switch_config[index_a:].find(current_search_pattern)

    if index_b == -1:
        print("Error: Could not locate Infrastructure port Information, exiting.")
        exit()

    #now that we have determined the area of interest, isolate
    current_substring = switch_config[index_a:index_a+index_b]

    current_search_pattern = re.compile(r'([T][e][n][ ][^\s]+)')

    infrastructure_ports = list()
    infrastructure_interfaces = list()
    flagged_infrastructure_interfaces = list()

    #check for the ports we care about and build an interface list
    for infrastructure_port in re.finditer(current_search_pattern, current_substring):
        if infrastructure_port.group(1) not in infrastructure_ports:
            infrastructure_ports.append(infrastructure_port.group(1))
            infrastructure_interfaces.append("interface TenGigabitEthernet" + infrastructure_port.group(1)[4:])

    #examine each infrastructure interface
    for infrastructure_interface in infrastructure_interfaces:
        index_a = switch_config.find(infrastructure_interface)
        index_b = switch_config[index_a:].find("!")
        current_substring = switch_config[index_a:index_a+index_b]

        #if the interface has something we don't like, we can flag it
        if current_substring.find("authentication") != -1:
            flagged_infrastructure_interfaces.append(("Authentication enabled on infrastructure interface " + infrastructure_interface, infrastructure_interface))

        if current_substring.find("dot1x") != -1:
            flagged_infrastructure_interfaces.append(("802.1.x enabled on infrastructure interface " + infrastructure_interface, infrastructure_interface))

        print(current_substring)

    if len(infrastructure_ports) == 0 or len(infrastructure_interfaces) == 0:
        print("Error: Could not locate any infrastructure ports/interfaces, exiting.")
        exit()

    #now, we can examine each non-infrastructure interface for compliance
    current_search_pattern = "show run"
    index_a = switch_config.find(current_search_pattern)

    if index_a == -1:
        print("Error: Could not locate run configuration, exiting.")
        exit()

    current_substring = switch_config[index_a:]

    #find all interface names after a new line/return character
    current_search_pattern = re.compile(r'[\n\r]([i][n][t][e][r][f][a][c][e][ ][^Vv].*)', re.MULTILINE)

    #string list of all NON infrastructure interfaces
    interfaces = list()

    #PAIR list of all flagged interfaces, with STRING reason, STRING interface
    flagged_interfaces = list()

    for interface in re.finditer(current_search_pattern, current_substring):
        if str(interface.group(1)) not in infrastructure_interfaces:
            interfaces.append(str(interface.group(1)))
            #isolate the configuration for each interface
            index_a = current_substring.find(str(interface.group(1)))
            index_b = current_substring[index_a:].find("!")

            #contains the interface substring
            interface_substring = current_substring[index_a:index_a+index_b]
            interface_lines = interface_substring.count('\n')

            #see if the interface is even configured
            if interface_lines is 1:
                flagged_interfaces.append(str(interface.group(1)) + " contains an empty configuration.", infrastructure_interface))
                print("dongers")

            print(interface_substring + "\n" + "Number of lines: " + str(interface_lines))

    print("bing")


finally:
    switch_config_file.close()
