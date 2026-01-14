
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

def generateCommandData(tx_fs, ask_percent, flagBits, commandCode, maskLength):

    rf_reset_length = round((8160e-6)/(1/tx_fs))
    data_bytes = [flagBits, commandCode, maskLength]
    CRC = calculateCRC(data_bytes)

    ## Rearrange Bits for Transmission
    flagBits = bin(flagBits)[2:].zfill(8)
    commandCode = bin(commandCode)[2:].zfill(8)
    maskLength = bin(maskLength)[2:].zfill(8)
    print(flagBits + commandCode + maskLength + CRC)
    rearranged_flagBits = ''
    for i in range(len(flagBits) - 1, 0, -2):
        bitpair = flagBits[i-1:i+1]
        rearranged_flagBits = rearranged_flagBits + bitpair

    rearranged_commandCode = ''
    for i in range(len(commandCode) - 1, 0, -2):
        bitpair = commandCode[i-1:i+1]
        rearranged_commandCode = rearranged_commandCode + bitpair

    rearranged_maskLength = ''
    for i in range(len(maskLength) - 1, 0, -2):
        bitpair = maskLength[i-1:i+1]
        rearranged_maskLength = rearranged_maskLength + bitpair

    rearranged_CRC = ''
    for i in range(len(CRC) - 1, 0, -2):
        bitpair = CRC[i-1:i+1]
        rearranged_CRC = rearranged_CRC + bitpair

    command = rearranged_flagBits + rearranged_commandCode + rearranged_maskLength + rearranged_CRC
    command_data = modulateCommand(command, tx_fs, ask_percent)
    command_data = modulateSOF_EOF(command_data, tx_fs, ask_percent)
    command_data = modulateSlotData(command_data, tx_fs, ask_percent, flagBits)
    
    command_data = np.append(command_data, np.zeros(rf_reset_length,)); #Add RF Reset after command
    
    command_data = addSineWave(command_data, tx_fs, 166.66)
    return command_data

def calculateCRC(data_bytes):
    # Constants
    POLYNOMIAL = 0x8408  # x^16 + x^12 + x^5 + 1
    PRESET_VALUE = 0xFFFF
    NUMBER_OF_BYTES = len(data_bytes)
    
    current_crc_value = PRESET_VALUE
    
    for i in range(NUMBER_OF_BYTES):
        current_crc_value = current_crc_value ^ (data_bytes[i])
        for j in range(8):
            if (current_crc_value & 0x0001):
                current_crc_value = (current_crc_value >> 1) ^ POLYNOMIAL
            else:
                current_crc_value = current_crc_value >> 1

    inverted_crc_value = ~current_crc_value
    unsigned_integer = inverted_crc_value+(1 << 16) 
    CRC = bin(unsigned_integer)[2:].zfill(16)

    return CRC
        
def modulateCommand(command, tx_fs, ask_percent):
    
    pair_samples = round((75.52e-6)/(1/tx_fs))
    low_percent = 1 - ask_percent
    low_samples = round((9.44e-06)/(1/tx_fs))
    low_data = np.ones(low_samples) * low_percent
    
    data = []
    for i in range(0, len(command), 2):
        pair = command[i:i+2]
        pair_data = np.ones(pair_samples)
        match pair:
            case "00":
                high_samples = round((9.44e-06)/(1/tx_fs))
                pair_data[high_samples:high_samples+low_samples] = low_data
            case "01":
                high_samples = round((28.32e-06)/(1/tx_fs))
                pair_data[high_samples:high_samples+low_samples] = low_data
            case "10":
                high_samples = round((47.2e-06)/(1/tx_fs))
                pair_data[high_samples:high_samples+low_samples] = low_data
            case "11":
                high_samples = round((66.08e-06)/(1/tx_fs))
                pair_data[high_samples:high_samples+low_samples] = low_data
        data = np.append(data, pair_data)
    return data

def modulateSOF_EOF(data, tx_fs, ask_percent):
    SOF_length = round((75.52e-06)/(1/tx_fs))
    EOF_length = round(SOF_length/2)
    
    low_percent = 1-ask_percent
    low_samples = round((9.44e-06)/(1/tx_fs))
    low_data = np.ones(low_samples) * low_percent

    SOF = np.ones(SOF_length)
    SOF[:low_samples] = low_data
    high_samples = round((47.2e-06)/(1/tx_fs))
    SOF[high_samples:high_samples+low_samples] = low_data

    EOF = np.ones(EOF_length)
    high_samples = round((18.88e-06)/(1/tx_fs))
    EOF[high_samples:high_samples + low_samples] = low_data

    data = np.append(SOF, data)
    data = np.append(data, EOF)
    return data

def modulateSlotData(data, tx_fs, ask_percent, flagBits):
    slot_flag = flagBits[2]
    rate_flag = flagBits[6]
    inv_flag = flagBits[5]
    
    low_percent = 1-ask_percent
    low_samples = round((9.44e-06)/(1/tx_fs))
    low_data = np.ones(low_samples) * low_percent

    EOF_length = round((37.76e-06)/(1/tx_fs))
    EOF = np.ones(EOF_length)
    high_samples = round((18.88e-06)/(1/tx_fs))
    EOF[high_samples:high_samples + low_samples] = low_data

    if (rate_flag == '1'):
        slot_length = round(8160e-06/(1/tx_fs))
    else:
        slot_length = round(20332e-06/(1/tx_fs))
    slot = np.ones(slot_length)
    data = np.append(slot, data)
    if (slot_flag == '0' and inv_flag == '1'):
        slot = np.append(slot,EOF)
        for i in range(16):
            data = np.append(data, slot)
    else:
        data = np.append(data, np.ones(slot_length))
    return data

def addSineWave(data, tx_fs, sinewave_fs):
    data_length = len(data)
    duration = data_length / tx_fs
    t = np.linspace(0, duration, data_length, endpoint=False, dtype=np.complex64)  # Time array
    # Generate the complex sine wave
    sine_wave = np.exp(2j * np.pi * sinewave_fs * t).astype(np.complex64)
    data = sine_wave * data
    return data

if __name__ == "__main__":
    tx_fs = 12.5e6
    ask_percent = 1
    flagBits = 0b00100111
    commandCode = 0b00000001
    maskLength = 0b00000000
    command_data = generateCommandData(tx_fs, ask_percent, flagBits, commandCode, maskLength)
    command_data = command_data.astype(np.complex64)
    # file_path = './test_command.dat'
    # command_data.tofile(file_path)