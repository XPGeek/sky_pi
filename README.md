# sky_pi

https://github.com/XPGeek/sky_pi

Intro:

The name of the configuration file determines the hardware type.

The prefix "IE" usually designates a firewall, and a switch model number, for example "3850" designates a switch.

The process should be the same regardless, however.

Process:

Look for the string "show cdp nei | e SEP"

Any of the ports listed under this command are ones we care about.
Duplicate ports are alright, just make sure the number of unique ports match the number after "total CDP entries"

If we care about the port, search for the unique ID of the port, the X/X/X number later in the document, interface ______X/X/X

Now, we can inspect the configuration of the interface (or the port we care about).

A “!” below the interface means there are no conditions set for this interface, FLAG this.

Note the description of the interface (do we care about this??)

Check to ensure that the number after "switchport access vlan" (or XXX) matches the number after the “authentication event server dead action reinitialize vlan”

“show authen session” shows all the ports and their authentication status. Check to ensure that the string “Unauth” doesn’t not exist here, if it does, we need to see which line and then flag it.
