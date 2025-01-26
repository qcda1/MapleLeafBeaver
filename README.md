# MapleLeafBeaver
## Maple Leaf Beaver 48VDC 100Ah LiFePO4 battery data acquisition module

<img width="709" alt="Capture d’écran, le 2025-01-26 à 16 17 07" src="https://github.com/user-attachments/assets/d4dba9e6-7269-456e-a4b6-d3098938aa78" />

The following module is meant to allow a Python programmer to acquire operating data from the battery's BMS for monitoring and archiving/reporting requirements. It is simple to use and provide inquiry functions that return battery operation parameters in the form of a Python dictionary (dict).

The communication protocol used at the network layer is RS485. This module was developed on a Raspberry Pi4 using a USB to RS485 converter such as:

<img width="589" alt="CANalyst-II" src="https://github.com/user-attachments/assets/5d50dd73-3f2a-451b-a499-af504f799a08" />
<img width="285" alt="USB-RS485" src="https://github.com/user-attachments/assets/b54d1531-e68d-44fb-9883-da0b9ccab3b0" />


## BMS protocol
With the use of the battery monitoring software provided by Maple Leaf and Wireshark USB communication sniffer program, I was able to determine the the BMS uses a subset of Pylontech RS485 protocol to expose operating data to an external program. This is valid for a certain amount of the available information.The BMS also respond to another set of commands that I have not yet identified.

This first implementation of the module provide functions to get the following two sets of operating data:
- Get analog value, fixed point (CID2=42<sub>H</sub>)
- Get system parameter, fixed point (CID2=47<sub>H</sub>)

Included in this repository is a document detailing the protocol used here. It is based on multiple annotated PDF Chinese documents.

## MapleLeafBeaver usage and example
