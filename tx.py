import os
import re
import serial
import time

# Config Port FOR /dev/pts/
port = 2
ser = serial.Serial('/dev/pts/' + str(port))

# DEFAULTS INTS VALUES
SOH = 0x01     #SOH -> Start of header character (decimal 1).
ACK = 0x06
NAK = 0x15
CAN = 0x18
EOT = 0x04     #EOT

# DEFAULT ASCII VALUES
asc_SOH  =   chr(SOH)
asc_ACK  =   chr(ACK)
asc_NAK  =   chr(NAK)
asc_EOT  =   chr(EOT)
asc_CAN  =   chr(CAN)

# OTHER VARS
SUB = '.'

## Functions ##

# Split string in peaces of 128 bits
def splitString(string):
    return [string[i:i+128] for i in range(0, len(string), 128)]
    
# Get Text of File
def getFileText(filename):
	with open(filename, 'r') as file:
		text = file.read()
	return splitString(text)

# Menu of TX
def menu(ser):
    print "Welcome to program TX (XMODEM) port: /dev/pts/" + str(port)
    print "Choose:"
    print "1 - Send File"
    print "2 - EOT"

    options = 0
    while (options == 0):
        options = int(input("Opt: "))
        if (int(options) == 2):
            ser.write(asc_EOT)
            quit()
        if (options != 1):
            options = 0

while True:
    menu(ser)
    os.system('cls||clear')

    # Count for packages of 128 bytes
    cont = 0x01

    # Open file
    filename = str(raw_input('Enter the file name and extension: '))
    DATAFULL = getFileText(filename)
    for DATA in DATAFULL:
        SEQ = cont          #SEQ -> one byte sequence number which starts at 1, and increments by one until it reaches 255 and then wraps around to zero.
        CSEQ = 255 - SEQ    #-SEQ
        asc_SEQ  =   chr(SEQ)
        asc_CSEQ =   chr(CSEQ)
        RESP = asc_NAK

        # Wait receiver send FIRST NAK
        if cont == 1:
            os.system('cls||clear')
            print "blocks to send: " + str(len(DATAFULL))
            print "Waiting First NAK...\n"
            FIRST = ser.read(1)
            time.sleep(1)
            os.system('cls||clear')
        else:
            FIRST = asc_ACK

        while (RESP == asc_NAK or FIRST == asc_NAK):
            # ---- #
            # Send SOH
            ser.write(chr(SOH))   
            print "SOH sent!"

            # Send SEQ and -SEQ
            ser.write(chr(SEQ))
            print "SEQ sent! package: " + str(hex(SEQ))
            ser.write(chr(CSEQ))
            print "-SEQ sent! value: " + str(hex(CSEQ))

            # ---- #
            #DATA -> 128, 8 bit bytes of data.
            if len(DATA) < 128:
                for i in range (len(DATA),  128):
                    DATA += SUB
            
            print "DATA: '" + DATA + "' -> Size: " + str(len(DATA))
            ser.write (DATA)  # SEND DATA

            # ---- #
            #FCS -> one byte sum of all of the data bytes
            s = 0
            for i in DATA:
                s = s + ord(i)
            FCS = s % 256
            asc_FCS = chr(FCS) 
            print "FCS -> " + str(FCS)

            ser.write(asc_FCS)  # SEND FCS 
            total = len(asc_SOH) + len(asc_SEQ) + len(asc_CSEQ) + len(DATA) + len(asc_FCS)
            print "TOTAL: " + str(total) + " bytes sent"
            FIRST = chr(0x0)

            # Get Status
            print "\nWaiting ACK"
            RESP = ser.read(1)
            if RESP == asc_ACK:
                print "Package sent sucessfully\n"
            elif RESP == asc_NAK:
                print "Failed to send package\n"
            elif RESP == asc_CAN:
                print "Canceled\n"
                quit()
            print "\n--------------------------"
            print "--------------------------\n"
        cont += 1

    # SEND EOT
    RESP = asc_NAK
    while (RESP == asc_NAK):
        ser.write(asc_EOT)
        RESP = ser.read(1)
        if RESP == asc_ACK:
            print "File uploaded successfully!\n"
        elif RESP == asc_NAK:
            print "Failed to send the file, trying again.\n"
        elif RESP == asc_CAN:
            print "Canceled\n"
            quit()


    # Wait for continue
    raw_input("Press Enter to continue...")
    os.system('cls||clear')
