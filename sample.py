# Sample program to print MapleLeaf Beaver battery data
# Assume that a battery is at pack address 0 for a single
# battery installation or the first of a multi pack bank. 

from MapleLeafBeaver import MapleLeafBeaver
import logging
import pprint

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("Sample")

p = MapleLeafBeaver("/dev/ttyUSB2", 9600)

pprint.pp(p.get_system_parameters("00"))

pprint.pp(p.get_values("00"))
