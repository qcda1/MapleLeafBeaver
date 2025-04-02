# MapleLeafBeaver
## Maple Leaf Beaver 48VDC 100Ah LiFePO4 battery data acquisition module

<img width="709" alt="Capture d’écran, le 2025-01-26 à 16 17 07" src="https://github.com/user-attachments/assets/d4dba9e6-7269-456e-a4b6-d3098938aa78" />

The following module is meant to allow a Python programmer to acquire operating data from the battery's BMS for monitoring and archiving/reporting requirements. It is simple to use and provide inquiry functions that return battery operation parameters in the form of a Python dictionary (dict).

The communication protocol used at the network layer is RS485. This module was developed on a Raspberry Pi4 using a USB to RS485 converter such as:

<img width="150" alt="USB-RS485" src="https://github.com/user-attachments/assets/700b02ee-b9ce-4ee4-8112-9c86c05fcfe0" />
<img width="150" alt="WaveShare1" src="https://github.com/user-attachments/assets/07b59fe4-521b-4cc6-9f26-51c1745c5972" />


## BMS protocol
With the use of the battery monitoring software provided by Maple Leaf and Wireshark USB communication sniffer program, I was able to determine the the BMS uses a subset of Pylontech RS485 protocol to expose operating data to an external program. This is valid for a certain amount of the available information.The BMS also respond to another set of commands that I have not yet identified.

This first implementation of the module provide functions to get the following two sets of operating data:
- Get analog value, fixed point (CID2=42<sub>H</sub>). Most if not all useful operational values are in this command.
- Get system parameter, fixed point (CID2=47<sub>H</sub>). Note that data from that command is not clean all the way. Need to study further.

Included in this repository is a document detailing the protocol used here. It is based on multiple annotated PDF Chinese documents.

## MapleLeafBeaver usage and example

Although it runs well, the module require some additional work with the logging function... I still need to understand the workings of looggers when used in classes... Still, logging works for errors but the line number where the error occured is wrong... If the set up permits, the module will work fine.

By default, the module can be called as is with a main routine that will print battary data for a bank of four batteries. For a different configuration you can modify the code in accordance to the number of batteries you have in your bank. Note that a future release will automatically determine the configuration.

You will need pprint (Pretty Print) module to run the sameple. Just pip install it.

In your program, simply import the module and use its functions to acquire battery data. Function usage is documented in the code.
Run and look at the sample.py programm for a minimal usage example.

