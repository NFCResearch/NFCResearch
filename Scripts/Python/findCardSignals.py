import numpy as np
import matplotlib.pyplot as plt

def findCardSignals(data,rx_fs, tx_fs, flagBits, tx_len):
    abs_data = np.abs(data)

    rate_flag = flagBits[6]

    if rate_flag == '1':
        slot_length = round(8160e-06/(1/rx_fs))
    else:
        slot_length = round(20332e-06/(1/rx_fs))

    rf_reset_length = round(8160e-06/(1/rx_fs))
    command_time = tx_len / tx_fs
    command_length = round((command_time/(1/rx_fs)) + (2.5e-04/(1/rx_fs)))
    N = 50
    rho = 15

    match flagBits[6:8]:
        case '00':
            SOF_time = (151.04e-06) * 4
            SOF_low_time = (56.64e-06) * 4
            bit_time = (37.76e-06) * 4
        case '01':
            SOF_time = (149.85e-06) * 4
            SOF_low_time = 0
            bit_time = (37.46e-06) * 4
        case '10':
            SOF_time = 151.04e-06
            SOF_low_time = 56.64e-06
            bit_time = 37.76e-06
        case '11':
            SOF_time = 149.85e-06
            SOF_low_time = 0
            bit_time = 37.46e-06

    SOF_length = round(SOF_time/(1/rx_fs))
    SOF_low_length = round(SOF_low_time/(1/rx_fs))
    bit_length = round(bit_time/(1/rx_fs))
    response_bits = 8
    response_length = SOF_length + (bit_length * (response_bits))
    tx_start = 0
    card_signals = [None] * response_length
    start = findRFreset(data)
    data = data[start:]
    while ((tx_start+(2*command_length)) < len(abs_data)):
        abs_data = np.abs(data)
        for i in range(0,len(abs_data), 100):
            delta = np.abs(abs_data[i+100] - abs_data[i])
            if delta > 0.1:
                tx_start = i
                break
        offset = tx_start + (command_length - slot_length - rf_reset_length)
        
        response_start = findResponseStart(data[offset:], N , rho)
        offset = offset + response_start - SOF_low_length
        
        card_signal = data[offset:offset + response_length]
        card_signals = np.vstack((card_signals,card_signal))
        
        data = data[tx_start + command_length - rf_reset_length:]
        
        start = findRFreset(data)
        data = data[start:]
    card_signals = card_signals[1:]
    return card_signals
    

def findResponseStart(data, N, rho):
    data = np.abs(data)
    delta = np.abs(np.diff(data))
    midPoint = int(np.floor(N/2) + 1)
    deltaSegment = delta[midPoint:N]
    sigma = rho * np.mean(deltaSegment)
    start = np.where(delta > sigma)[0][0]
    return start

def findRFreset(data):
    for i in range(0, len(data), 100):
            avg = np.mean(abs(data[i:i+100]))
            if avg <= 0.001:
                return i
                


def plot(data):
    plt.figure(figsize=(10, 6))  # Create a new figure with a specific size
    plt.plot(abs(data), label='Command_data')  # Plot the data
    plt.grid(True)  # Show grid
    plt.show()  # Display the plot

if __name__ == "__main__":
    # Example of reading the binary file back into a NumPy array
    data = np.load("../GNURadio/Data/OneHigh_/buf.npy", allow_pickle=True)
    command = np.fromfile("./test_command.dat", dtype=np.complex64)
    card_signals = findCardSignals(data, 2e6, 12.5e6, '00100111', len(command))
    print(len(command))
    print(card_signals.shape)
    # plot(card_signals[54])
    

    