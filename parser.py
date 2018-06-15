#!/usr/bin/env python

import csv
import re
import sys

try:

    #Open File for reading:
    switch_config_file = open(sys.argv[1], 'r')
    switch_config = switch_config_file.read()

    #Open File for writing:
    output_file = open('switch_report.csv', 'w', newline='')
    field_names = ['interface', 'description', 'error']

    csv_writer = csv.DictWriter(output_file, fieldnames=field_names)
    csv_writer.writeheader()

    #look for infrastructure_port information
    index_a = switch_config.find("show cdp nei | e SEP")

    if index_a == -1:
        print("Error: Could not locate the 'show cdp nei | e SEP' command, exiting.")
        exit()

    index_b = switch_config[index_a:].find("Total cdp entries displayed :")

    if index_b == -1:
        print("Error: Could not locate the end of the 'show cdp nei | e SEP' command, exiting.")
        exit()

    #now that we have determined the area of interest, isolate
    current_substring = switch_config[index_a:index_a+index_b]

    current_search_pattern = re.compile(r'([T][e][n][ ][^\s]+)')

    infrastructure_ports = list()
    infrastructure_interfaces = list()
    flagged_interfaces = list()

    #check for the ports we care about and build an interface list
    for infrastructure_port in re.finditer(current_search_pattern, current_substring):
        if infrastructure_port.group(1) not in infrastructure_ports:
            infrastructure_ports.append(infrastructure_port.group(1))
            infrastructure_interfaces.append("interface TenGigabitEthernet" + infrastructure_port.group(1)[4:])

    if len(infrastructure_ports) == 0 or len(infrastructure_interfaces) == 0:
        print("Error: Could not locate any infrastructure ports or interfaces, exiting.")
        exit()

    #examine each infrastructure interface
    for infrastructure_interface in infrastructure_interfaces:

        #index_a - index that starts the infrastructure interface
        index_a = switch_config.find(infrastructure_interface)
        #index_b - index that ends the infrastructure interface
        index_b = switch_config[index_a:].find("!")

        #contains the interface configuration
        current_substring = switch_config[index_a:index_a+index_b]

        #infrastructure interfaces should never have authentication enabled
        if current_substring.find("authentication") != -1:
            flagged_interfaces.append("Authentication enabled on infrastructure interface " + infrastructure_interface)

        if current_substring.find("dot1x") != -1:
            flagged_interfaces.append("802.1.x enabled on infrastructure interface " + infrastructure_interface)

    #now, we can examine each non-infrastructure interface for compliance
    current_search_pattern = "show run"
    index_a = switch_config.find(current_search_pattern)

    if index_a == -1:
        print("Error: Could not locate the 'show run' command, exiting.")
        exit()

    current_substring = switch_config[index_a:]

    #find all interface names after a new line/return character
    current_search_pattern = re.compile(r'[\n\r]([i][n][t][e][r][f][a][c][e][ ][^Vv].*)', re.MULTILINE)

    for interface in re.finditer(current_search_pattern, current_substring):
        if str(interface.group(1)) not in infrastructure_interfaces:
            #isolate the configuration for each interface

            #contains the interface substring
            interface_substring = current_substring[interface.start():interface.start() + current_substring[interface.start():].find("!")]
            interface_lines = interface_substring.count('\n') - 1

            #print("interface_substring:\n" + interface_substring + "\ninterface_lines: " + str(interface_lines) + "\n")

            #see if the interface is even configured
            if interface_lines is 1:
                csv_writer.writerow({'interface': interface.group(1), 'description': "N/A", 'error': "Has an empty configuration."})
                #flagged_interfaces.append(str(interface.group(1)) + " has an empty configuration.")
                continue
            else:
                current_search_pattern = re.compile(r'[\n\r]([ ][d][e][s][c][r][i][p][t][i][o][n][ ]).*')
                description = re.search(current_search_pattern, interface_substring)

                if description is not None:
                    description_substring = interface_substring[description.start() + 14:description.end()]
                else:
                    description_substring = "N/A"

            #now, search for the vlan key command
            current_search_pattern = "switchport access vlan"
            index_a = interface_substring.find(current_search_pattern)

            #if it doesn't have one, note it
            if index_a == -1:
                csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "Non-empty configuration, but does not have an access VLAN configured."})
                #flagged_interfaces.append(str(interface.group(1)) + " does not have an empty configuration, but does not have an access VLAN configured.")
            else:
                #non-greedy regex to find the first numerical numbers on the line where the command switchport access vlan
                current_search_pattern = re.compile(r'[0-9]+')
                vlan_access_number = re.search(current_search_pattern, interface_substring[index_a:])

                if vlan_access_number is None:
                    csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "No VLAN number associated with the access command."})
                    #flagged_interfaces.append(str(interface.group(1)) + " does not have a VLAN number associated with the access command.")
                else:
                    #now, search for the "other" vlan key command
                    current_search_pattern = "authentication event server dead action reinitialize vlan"
                    index_a = interface_substring.find(current_search_pattern)

                    #if it doesn't have one, note it
                    if index_a == -1:
                        csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "Does not have dead action reinitialize VLAN configured."})
                        #flagged_interfaces.append(str(interface.group(1)) + " does not have dead action reinitialize VLAN configured.")
                    else:
                        #non-greedy regex to find the first numerical numbers on the line where the command switchport access vlan
                        current_search_pattern = re.compile(r'[0-9]+')
                        vlan_dead_access_number = re.search(current_search_pattern, interface_substring[index_a:])

                        if vlan_dead_access_number is None:
                            csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "No VLAN number associated with the dead action reinitialize VLAN."})
                            #flagged_interfaces.append(str(interface.group(1)) + " does not have a VLAN number associated with the dead action reinitialize VLAN.")
                        else:
                            if vlan_access_number.group(0) != vlan_dead_access_number.group(0):
                                csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "Has mismatched VLAN numbers for access/dead action reinitialize VLANs."})
                                #flagged_interfaces.append(str(interface.group(1)) + " has mismatched VLAN numbers for access and dead action reinitialize VLANs.")

            # authentication order mab dot1x
            # authentication priority dot1x mab

            index_a = interface_substring.find("authentication order dot1x mab") #incorrect
            index_b = interface_substring.find("authentication order mab dot1x") #correct

            if index_a != -1 and index_b == -1: #an incorrect configuration was found
                csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "Incorrect authentication order."})
                #flagged_interfaces.append(str(interface.group(1)) + " has an incorrect authentication order.")

            if index_a == -1 and index_b == -1: #no authentication configuration was found
                csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "No authenticaion order specified."})
                #flagged_interfaces.append(str(interface.group(1)) + " does not have an authenticaion order specified.")

            index_a = interface_substring.find("authentication priority dot1x mab") #correct

            if index_a == -1:
                csv_writer.writerow({'interface': interface.group(1), 'description': description_substring, 'error': "No authentication priority specified."})
                #flagged_interfaces.append(str(interface.group(1)) + " does not have an authentication priority specified.")

    index_a = switch_config.find("show authen session")

    if index_a == -1:
        csv_writer.writerow({'interface': str(sys.argv[1]), 'description': "SWITCH_WIDE", 'error': "The switch configuration doesn't have a valid authenticaion session information."})
        #flagged_interfaces.append("Error: " + str(sys.argv[1]) + " does not have a valid authenticaion session information.")

    authentication_substring = switch_config[index_a: index_a + switch_config[index_a:].find("Session count =")]

    index_a = authentication_substring.find("UnAuth")

    if index_a != -1:
        csv_writer.writerow({'interface': str(sys.argv[1]), 'description': "SWITCH_WIDE", 'error': "The switch has an unauthenticated session."})
        #flagged_interfaces.append("Error: " + str(sys.argv[1]) + " has an unauthenticated session.")

finally:
    switch_config_file.close()
    output_file.close()
