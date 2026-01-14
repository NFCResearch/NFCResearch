import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import interp1d

def plot(data):
    plt.figure(figsize=(10, 6))  # Create a new figure with a specific size
    plt.plot(abs(data), label='Command_data')  # Plot the data
    plt.grid(True)  # Show grid
    plt.show()  # Display the plot

def plotBuf():
    path = data_directory / 'buf.npy'
    data = np.load(path, allow_pickle=True)
    print(data.shape)
    plot(data)
    
def plotCardSignals(signals, data):


    print(data.shape)
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    print(signals)
    for i in signals:
        plt.plot(abs(data[i]))

    # Customize the plot
    plt.xlabel('Time')  # Label for x-axis
    plt.ylabel('Amplitude')  # Label for y-axis
    plt.title('Overlapping Plots of card_signals')  # Plot title
    plt.grid(True)  # Display grid lines on the plot
    plt.legend([f'Signal {i+1}' for i in range(data.shape[0])])  # Add legend with labels

    plt.show()

def plotCardSignal(card_signal):
    path = data_directory / 'card4.npy'
    data = np.load(path, allow_pickle=True)
    print(data[card_signal].shape)
    plot(data[card_signal])

def plotDatFile():
    data = np.fromfile("../GNURadio/Data/rx_data.dat", np.complex64)
    plot(data)


def differences(arr1, arr2):
    windows_size = 100
    diffs = []
    for i in range(0,len(arr1)-windows_size, windows_size):
        arr1_mean = np.mean(np.abs(arr1[i:i+windows_size]))
        arr2_mean = np.mean(np.abs(arr2[i:i+windows_size]))
        diff = np.abs(arr1_mean - arr2_mean)
        diffs = np.append(diffs, diff)
    return np.mean(diffs)


# card = "card52.npy"
# data_directory = Path('C:/Users/Dickson/Documents/Research_Summer2024/DataCollection/GNURadio/Data/OneLow_')
# path = data_directory / card
# data = np.load(path, allow_pickle=True)
# plotCardSignals(range(0,500),data)

# data_directory = Path('C:/Users/Dickson/Documents/Research_Summer2024/DataCollection/GNURadio/Data/TwoLow_')
# path = data_directory / card
# data = np.load(path, allow_pickle=True)
# plotCardSignals(range(0,500),data)


# data_directory = Path('C:/Users/Dickson/Documents/Research_Summer2024/DataCollection/GNURadio/Data/OneHigh_')
# path = data_directory / card
# data = np.load(path, allow_pickle=True)
# plotCardSignals(range(0,500),data)


# data_directory = Path('C:/Users/Dickson/Documents/Research_Summer2024/DataCollection/GNURadio/Data/TwoHigh_')    
# path = data_directory / card
# data = np.load(path, allow_pickle=True)
# plotCardSignals(range(0,500),data)


# corr_path = data_directory / 'corr_signal.npy'

# corr_signal = np.load(corr_path, allow_pickle=True)

# card_path = data_directory / 'card_signals.npy'
# save_path = data_directory / 'corr_signal.npy'
# data = np.load(card_path, allow_pickle=True)
# np.save(save_path, data[40])
# print('Signal Saved to: ' + str(save_path))

# plotDatFile()
npy_data = np.load("../GNURadio/Realtime_Prediction/input_data.npy", allow_pickle=True)

response0 = np.load("../GNURadio/Realtime_Prediction/response0.npy", allow_pickle=True)
response1 = np.load("../GNURadio/Realtime_Prediction/response1.npy", allow_pickle=True)
response2 = np.load("../GNURadio/Realtime_Prediction/response2.npy", allow_pickle=True)
response3 = np.load("../GNURadio/Realtime_Prediction/response3.npy", allow_pickle=True)
responses = np.concatenate((response0,response1,response2,response3))
print(response0.shape)
print(response1.shape)
print(response2.shape)
print(response3.shape)
print(responses.shape)

# rx_data = np.fromfile("../GNURadio/Realtime_Prediction/prediction_data.dat", np.complex64)
plt.figure(2)
plt.plot(abs(responses))
plt.show()

