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
Run and look at the sample.py program for a minimal usage example.

### Example of running MapleLeafBeaver.py as is from the command line and on a battery bank of four packs:

    pi@rasp02:~/MapleLeafBeaver $ python MapleLeafBeaver.py


    Key                            P0                        P1                        P2                        P3                       
    ================================================================================================================================
    dtm                            2025-04-02 09:54:02       2025-04-02 09:54:02       2025-04-02 09:54:02       2025-04-02 09:54:03      
    NPack                          0                         1                         2                         3                        
    UnitCellVoltage                29.5                      29.5                      29.5                      29.5                     
    UnitCellLowVoltageThreshold    27.0                      27.0                      27.0                      27.0                     
    UnitCellUnderVoltageThreshold  33.51                     33.51                     33.51                     33.51                    
    ChargeUpperLimitTemperature    -11.0                     -11.0                     -11.0                     -11.0                    
    ChargeLowerLimitTemperature    -11.0                     -11.0                     -11.0                     -11.0                    
    ChargeLowerLimitCurrent        120.0                     120.0                     120.0                     120.0                    
    UpperLimitOfTotalVoltage       57.6                      57.6                      57.6                      57.6                     
    LowerLimitOfTotalVoltage       49.0                      49.0                      49.0                      49.0                     
    UnderVoltageOfTotalVoltage     44.8                      44.8                      44.8                      44.8                     
    DischargeUpperLimitTemperature 65.0                      65.0                      65.0                      65.0                     
    DischargeLowerLimitTemperature 216.9                     216.9                     216.9                     216.9                    
    DischargeLowerLimitCurrent     49.0                      49.0                      49.0                      49.0                     


    Key        P0                   P1                   P2                   P3                  
    =============================================================================================
    dtm        2025-04-02 09:54:03  2025-04-02 09:54:03  2025-04-02 09:54:03  2025-04-02 09:54:04 
    NPack      0                    1                    2                    3                   
    NbCell     16                   16                   16                   16                  
    VCell1     3454                 3454                 3465                 3468                
    VCell2     3455                 3469                 3467                 3467                
    VCell3     3455                 3467                 3466                 3472                
    VCell4     3475                 3469                 3467                 3467                
    VCell5     3468                 3465                 3466                 3468                
    VCell6     3467                 3456                 3466                 3472                
    VCell7     3455                 3466                 3464                 3471                
    VCell8     3462                 3463                 3467                 3471                
    VCell9     3464                 3467                 3444                 3471                
    VCell10    3475                 3475                 3467                 3468                
    VCell11    3475                 3472                 3469                 3469                
    VCell12    3476                 3472                 3454                 3472                
    VCell13    3468                 3469                 3469                 3473                
    VCell14    3452                 3462                 3469                 3469                
    VCell15    3471                 3469                 3468                 3435                
    VCell16    3476                 3469                 3469                 3471                
    VTot       55.448               55.464               55.437               55.484              
    NbT        7                    7                    7                    7                   
    T1         12.4                 12.9                 12.3                 12.6                
    T2         12.4                 12.5                 12.7                 12.7                
    T3         12.7                 12.9                 12.7                 13.0                
    T4         12.6                 13.2                 13.1                 13.1                
    T5         14.4                 14.1                 13.9                 14.2                
    T6         13.9                 14.1                 13.8                 14.3                
    T7         13.5                 13.6                 13.4                 13.6                
    Current    0.0                  0.0                  0.0                  0.0                 
    BatVolt    55.41                55.39                55.44                55.43               
    RemCap     100.0                99.98                100.0                99.99               
    CapInd     4                    4                    4                    4                   
    TotCap     100.0                100.0                100.0                100.0               
    NbCycles   24                   25                   24                   27                  
    RemCapR    100                  99                   100                  99                  
    SOH        100                  100                  100                  100                 


### Example of running sample.py from a Raspberry Pi connected to my battery bank and inquiry first battery at address 00:

    pi@rasp02:~/MapleLeafBeaver $ python sample1.py
    {'dtm': '2025-04-02 09:44:18',
    'NPack': 0,
    'UnitCellVoltage': 29.5,
    'UnitCellLowVoltageThreshold': 27.0,
    'UnitCellUnderVoltageThreshold': 33.51,
    'ChargeUpperLimitTemperature': -11.0,
    'ChargeLowerLimitTemperature': -11.0,
    'ChargeLowerLimitCurrent': 120.0,
    'UpperLimitOfTotalVoltage': 57.6,
    'LowerLimitOfTotalVoltage': 49.0,
    'UnderVoltageOfTotalVoltage': 44.8,
    'DischargeUpperLimitTemperature': 65.0,
    'DischargeLowerLimitTemperature': 216.9,
    'DischargeLowerLimitCurrent': 49.0}
    {'dtm': '2025-04-02 09:44:18',
    'NPack': 0,
    'NbCell': 16,
    'VCell1': 3455,
    'VCell2': 3456,
    'VCell3': 3456,
    'VCell4': 3475,
    'VCell5': 3468,
    'VCell6': 3467,
    'VCell7': 3456,
    'VCell8': 3462,
    'VCell9': 3465,
    'VCell10': 3475,
    'VCell11': 3474,
    'VCell12': 3476,
    'VCell13': 3468,
    'VCell14': 3453,
    'VCell15': 3471,
    'VCell16': 3476,
    'VTot': 55.453,
    'NbT': 7,
    'T1': 12.4,
    'T2': 12.4,
    'T3': 12.8,
    'T4': 12.6,
    'T5': 14.4,
    'T6': 13.9,
    'T7': 13.5,
    'Current': 0.0,
    'BatVolt': 55.41,
    'RemCap': 100.0,
    'CapInd': 4,
    'TotCap': 100.0,
    'NbCycles': 24,
    'RemCapR': 100,
    'SOH': 100}
