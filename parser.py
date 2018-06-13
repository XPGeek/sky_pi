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

    if current_search_pattern == -1:
        print("Error: Could not locate Infrastructure port Information")
        exit()

    current_search_pattern = "Total cdp entries displayed :"
    index_b = switch_config[index_a:].find(current_search_pattern)

    if current_search_pattern == -1:
        print("Error: Could not locate Infrastructure port Information")
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

        if current_substring.find("authentication") != -1:
            flagged_infrastructure_interfaces.append(("Authentication enabled on infrastructure interface " + infrastructure_interface, infrastructure_interface))

        if current_substring.find("dot1x") != -1:
            flagged_infrastructure_interfaces.append(("802.1.x enabled on infrastructure interface " + infrastructure_interface, infrastructure_interface))

        print(current_substring)





finally:
    switch_config_file.close()
