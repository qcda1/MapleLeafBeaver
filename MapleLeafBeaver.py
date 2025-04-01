import serial
from serial.tools import list_ports
import time
import logging

class MapleLeafBeaver:
    """
    Module to get operational data from Maple Leaf Beaver 48VDC/100Ah LiFePO4 battery pack.
    The protocol is a subset of Pylontech protocol using RS485 as the physical communication layer.

    Example usage:
    from MapleLeafBeaver import MapleLeafBeaver
    p = MapleLeafBeaver() # Default is MapleLeafBeaver("/dev/ttyUSB2", 9600)
    p.get_values("00")
    p.get_system_parameters("00")

    The battery's BMS use a subset of Pylontech communication protocol on RS485. Functions defined
    in this modules simplify the data acquisition and provide results in the form of Python dict with
    a timestamp value as the first item of the dict.
    The user can then display and/or save the data in database for display, monitoring, archiving and analysis.

    The supported commands are the following:
    - Function: get_values(pack) get cell values and overall battery values
    - Function: get_system_parameters(pack) get battery parameters (still need some work)
    
    """

    class Logg:
        """Created class logg because I couldn't get log to be defined and accessible in the methods
        such as snd_cmd() and decode42()... Error was saying log was not defined or self.log was
        not defined, etc. Unfortunately, even if the addition of this class fixes the use of logging
        in the methods, it reports the line number of the following error() method instead of the
        line of origin where the error occured..."""

        def __init__(self, name="MapleLeafBeaver", level=logging.ERROR):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)

            # Configuration du handler
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)-5s %(module)s:%(lineno)s %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        def error(self, message, stack_info=True):
            self.logger.error(message)

        def info(self, message):
            self.logger.info(message)

        def debug(self, message):
            self.logger.debug(message)

        def warning(self, message):
            self.logger.warning(message)

    # Communication protocol frame fields details
    SOI = "~"  # Start Of Information
    VER = "21"  # Version du protocol
    ADR = "00"  # Numéro du pack
    CID1 = "46"  # MapleLeafBeaver Data
    CID2 = "42"  # Commande exemple: "42H = Get analog value, fixed point"
    LENGTH = "E002"  # LENGTH
    INFO = "00"  # INFO
    CHECKSUM = "FD31"
    EOI = "\r"  # End Of Information

    NBPACK = 3  # Number of packs in the battery bank

    def __init__(self, device="/dev/ttyUSB2", baudrate=9600):
        """
        Initialisation MapleLeafBeaver instance.

        :param device: Serial port device name (for exemple, '/dev/ttyUSB2'). Default value: "/dev/ttyUSB2"
        :param baudrate: Transmission speed in baud (for exemple, 9600). Default value: 9600
        """
        self.device = device  # Enregistrer le port série comme variable d'instance
        self.baudrate = baudrate  # Enregistrer le baudrate comme variable d'instance
        self.log = MapleLeafBeaver.Logg()

    @staticmethod
    def chkpack(pack):
        try:
            if int(pack) < 0 or int(pack) > MapleLeafBeaver.NBPACK:
                return False
        except:
            return False
        return True

    @staticmethod
    def snd_cmd(command, device, baudrate, log):
        ''' Send communication frame to BMS via RS485 interface and comm link.'''
        #        print(f"device: {device}, baudrate: {baudrate}")

        # Return code description dict
        desc = {
            0: 'Normal',
            1: 'VER error',
            2: 'CHKSUM error',
            3: 'LCHKSUM error',
            4: 'CID2 command invalid',
            5: 'Command format error',
            6: 'Invalid data',
            144: 'ADR error',
            145: 'Communication error',
        }

        command = (
            MapleLeafBeaver.SOI
            + command
            + MapleLeafBeaver.checksum(command)
            + MapleLeafBeaver.EOI
        )
        #    print("--sndcmd------------------------------------------------------------")
        #    print("command=", command)
        full_command = bytearray(command, "ascii")
        #    print("full_command=", full_command)
        #    print("full_command(Hex)=", full_command.hex())
        #    print("--------------------------------------------------------------------")
        try:
            with serial.serial_for_url(device, baudrate) as s:
                # print("Executing command via serialio...")
                s.timeout = 0.1
                s.write_timeout = 0.1
                s.flushInput()
                s.flushOutput()
                s.write(full_command)
                time.sleep(0.1)  # give serial port time to receive the data
                response_line = s.read_until(b"\r\n")
#                print("serial response is: %s", response_line.hex(':', 1), type(response_line), len(response_line), "\n")
                if int(response_line[7:9]) != 0:
                    log.error(f"Return code is not 0 in response_line... Error = {int(response_line[7:9])} and reason: {desc[int(response_line[7:9])]}")
                    return None
                return response_line
        except Exception as e:
            log.error(f"Serial read error: {e}")
            log.error(f"Command execution failed: {full_command}")
            return None


    # Fonction pour calculer la valeur du checksum
    @staticmethod
    def checksum(trame: str) -> str:
        """
        Checksum calculation as per Pylontech protocol definition.
        """
        #    print("trame=", trame)

        # Initialiser la somme ASCII
        checksum_sum = 0

        # Calculer la somme des valeurs ASCII des caractères restants
        for char in trame:
            checksum_sum += ord(char)
        #        print(checksum_sum, ord(char), end=';')

        # Appliquer le modulo 65536
        checksum_mod = checksum_sum % 65536
        #    print("checksum_mod=", checksum_mod)

        # Complément binaire (bitwise invert) et ajout de 1
        checksum = (~checksum_mod + 1) & 0xFFFF  # Limite à 16 bits
        #    print("checksum=", checksum)

        # Retourner en hexadécimal, avec 4 caractères (zéros à gauche si nécessaire)
        return f"{checksum:04X}"

    @staticmethod
    def decoder42(dtm, words, log):
        """Decode frame for command 42H: Get analog value, fixed point
        as per Pylontech communication protocol.
        Returns a dict with timestamp added as first keyed item."""
        try:
            c = 0
            t = 0
            temp = 0
            BD = {}  # MapleLeafBeaver Data
            BD["dtm"] = dtm
            # Numéro du pack
            BD["NPack"] = int(words[3 : 3 + 2].decode(), 16)
            # Nombre de cellules dans la batterie
            BD["NbCell"] = int(words[15 : 15 + 2].decode(), 16)
            # Voltage de chaque cellule en mV
            for i in range(17, 17 + 64, 4):
                c = c + 1
                mV = int(words[i : i + 4].decode(), 16)
                k = "VCell" + str(c)
                BD[k] = mV
                #            print("C" + str(c) + "=" + str(mV) + "mV, ", end="")
                t = t + mV
            BD["VTot"] = t / 1000
            # Nombre de sondes de températures
            BD["NbT"] = int(words[82:83])
            # Calcul des températures présentent en degrés Kelvin et converties en degrés Celcius
            c = 0
            for i in range(83, 83 + 28, 4):
                c = c + 1
                K = int(words[i : i + 4].decode(), 16)
                temp = (K - 2731) / 10
                #            print("t=" + str(temp) + "℃, ", end="")
                k = "T" + str(c)
                BD[k] = temp
            # Courant
            byte_value = bytes.fromhex(words[111 : 111 + 4].decode("utf-8"))
            signed_value = int.from_bytes(byte_value, byteorder="big", signed=True)
            BD["Current"] = signed_value / 100
            # Voltage de la batterie
            BD["BatVolt"] = int(words[115 : 115 + 4].decode(), 16) / 100
            # Capacité restante
            BD["RemCap"] = int(words[119 : 119 + 4].decode(), 16) / 100
            # Indicateur de capacité de la batterie
            BD["CapInd"] = int(words[123 : 123 + 2].decode(), 16)
            # Capacité totale
            BD["TotCap"] = int(words[125 : 125 + 4].decode(), 16) / 100
            # Nombre de cycles de charge
            BD["NbCycles"] = int(words[129 : 129 + 4].decode(), 16)
            # Capacité restante arrondie
            BD["RemCapR"] = int(words[133 : 133 + 2].decode(), 16)
            # SOH ou State Of Health
            BD["SOH"] = int(words[135 : 135 + 2].decode(), 16)
        except Exception as ex:
            log.error(f"Exception dans decoder42: {ex}")
            log.error(f"words: {words}")
            BD = None
        return BD

    @staticmethod
    def decoder47(dtm, words):
        """Decode frame for command 47H: Get system parameter, fixed point
        as per Pylontech communication protocol.
        Returns a dict with timestamp added as first keyed item.
        In the case of MapleLeaf Beaver batteries, these values are questionable"""

        try:
            #            print(words)
            BD = {}  # MapleLeafBeaver Data
            BD["dtm"] = dtm
            BD["NPack"] = int(words[3 : 3 + 2].decode(), 16) # Pack number 0-32
            BD["UnitCellVoltage"] = int(words[17 : 17 + 4].decode(), 16) / 100
            BD["UnitCellLowVoltageThreshold"] = int(words[21 : 21 + 4].decode(), 16) / 100
            BD["UnitCellUnderVoltageThreshold"] = int(words[25 : 25 + 4].decode(), 16) / 100
            BD["ChargeUpperLimitTemperature"] = (int(words[29 : 29 + 4].decode(), 16) - 2731) / 10
            BD["ChargeLowerLimitTemperature"] = (int(words[29 : 29 + 4].decode(), 16) - 2731) / 10
            BD["ChargeLowerLimitCurrent"] = int(words[33 : 33 + 4].decode(), 16) / 100
            BD["UpperLimitOfTotalVoltage"] = int(words[37 : 37 + 4].decode(), 16) / 100
            BD["LowerLimitOfTotalVoltage"] = int(words[41 : 41 + 4].decode(), 16) / 100
            BD["UnderVoltageOfTotalVoltage"] = int(words[45 : 45 + 4].decode(), 16) / 100
            BD["DischargeUpperLimitTemperature"] = (int(words[49 : 49 + 4].decode(), 16) - 2731) / 10
            BD["DischargeLowerLimitTemperature"] = (int(words[41 : 41 + 4].decode(), 16) - 2731) / 10
            BD["DischargeLowerLimitCurrent"] = int(words[41 : 41 + 4].decode(), 16) / 100

        except Exception as ex:
            log.error(f"Exception dans decoder47: {ex}")
            log.error(f"words: {words}")
            BD = None
        return BD

    def get_values(self, pack):
        """Get analog value, fixed point (42H) from pack number.
        Pack number is a str from '00' to '32'.
        """
        self.CID2 = "42"
        if MapleLeafBeaver.chkpack(pack):
            self.ADR = pack
        else:
            return {"Error-": 'Wrong pack number... Should be "00" to "03".'}
        dtm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        command = self.VER + self.ADR + self.CID1 + self.CID2 + self.LENGTH + self.INFO
        #        print("command:", command)
        response_line = MapleLeafBeaver.snd_cmd(
            command, self.device, self.baudrate, self.log
        )
        #        print("Réponse:", response_line, len(response_line))
        Dict = self.decoder42(dtm, response_line, self.log)

        return Dict

    def get_system_parameters(self, pack):
        """Get system parameter, fixed point (47H) from pack number.
        Pack number is a str from '00' to '03'.
        """
        self.CID2 = "47"
        if MapleLeafBeaver.chkpack(pack):
            self.ADR = pack
        else:
            return {"Error-": 'Wrong pack number... Should be "00" to "03".'}
        dtm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        command = self.VER + self.ADR + self.CID1 + self.CID2 + self.LENGTH + self.INFO
        #        print("command:", command)
        response_line = MapleLeafBeaver.snd_cmd(
            command, self.device, self.baudrate, self.log
        )
        #        print("Réponse:", response_line, len(response_line))
        Dict = self.decoder47(dtm, response_line)

        return Dict


if __name__ == "__main__":

    from serial.tools import list_ports
    import pprint

    logging.basicConfig(
        level=logging.WARNING,
    )
    log = logging.getLogger("MapleLeafBeaver")

    # Get device name from Linux
    def get_USB_device(name):
        """ Function to return the assigned port name as etc/ttyUSBx by supplying
            your device's iProduct name. Can be found with command lsusb -v | grep iProduct.
            Note that the name can change when adding or removing USB devices from the computer.
        """
        lstports = list_ports.comports(include_links=True)
        for port in lstports:
            if name in port.description:
                return port.device
        log.error("No communication port found...")
        return "None"


    p = MapleLeafBeaver(get_USB_device("USB2.0-Serial"), 9600)
    # print(p.get_protocol_version())
    # print(p.get_manufacturer_info())
    #pprint.pp(p.get_system_parameters("00"))
    #pprint.pp(p.get_system_parameters("01"))
    #pprint.pp(p.get_system_parameters("02"))
    #pprint.pp(p.get_system_parameters("03"))
    # print(p.get_management_info())
    # print(p.get_module_serial_number())
    # print(p.get_values())
    #pprint.pp(p.get_values("00"))
    #pprint.pp(p.get_values("01"))
    #pprint.pp(p.get_values("02"))
    #pprint.pp(p.get_values("03"))

    # Print get_system_parameters() output in four columns
    p0 = p.get_system_parameters("00")
    p1 = p.get_system_parameters("01")
    p2 = p.get_system_parameters("02")
    p3 = p.get_system_parameters("03")
    # Keys to print
    keys = p0.keys()
    # Header
    print(f"\n\n{'Key':<30} {'P0':<25} {'P1':<25} {'P2':<25} {'P3':<25}")
    print("=" * 128)
    # Affichage des valeurs alignées en colonnes
    for key in keys:        
        print(f"{key:<30} {p0[key]:<25} {p1[key]:<25} {p2[key]:<25} {p3[key]:<25}")

    # Print get_values() output in four columns
    p0 = p.get_values("00")
    p1 = p.get_values("01")
    p2 = p.get_values("02")
    p3 = p.get_values("03")
    # Keys to print
    keys = p0.keys()
    # Header
    print(f"\n\n{'Key':<10} {'P0':<20} {'P1':<20} {'P2':<20} {'P3':<20}")
    print("=" * 93)
    # Affichage des valeurs alignées en colonnes
    for key in keys:
        print(f"{key:<10} {p0[key]:<20} {p1[key]:<20} {p2[key]:<20} {p3[key]:<20}")

