#!/usr/bin/env python

import sys
import re

try:

    #Open File for reading:

    switch_config_file = open(sys.argv[1], 'r')
    switch_config = switch_config_file.read()

    #STEP 1
    #Look for infrastructure_port information

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
    print(str(index_a) + " " + str(index_b) + " is our substring index.")

    current_substring = switch_config[index_a:index_a+index_b]

    print(current_substring)

    current_search_pattern = re.compile(r'([T][e][n][ ][^\s]+)')

    for infrastructure_port in re.finditer(current_search_pattern, current_substring):
        print(infrastructure_port.group(1))

finally:
    switch_config_file.close()
