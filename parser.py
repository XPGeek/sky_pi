#!/usr/bin/env python

import sys
import re

try:
    junk_text = open(sys.argv[1], 'r')
    junk = junk_text.read()
    print(junk)

    email_list = open("list.txt", 'w')

    pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

    for email in re.finditer(pattern, junk):
        email_list.write(email.group(0))
        email_list.write('\n')

finally:
    junk_text.close()
