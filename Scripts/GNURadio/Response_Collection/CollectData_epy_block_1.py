"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt
import logging
import os
from pathlib import Path
from scipy.stats.stats import pearsonr 

logger = logging.getLogger('grc')
logging.basicConfig(level=logging.DEBUG)

class SaveNumpyArrayBlock(gr.sync_block):
    def __init__(self, rx_fs=2e6, tx_fs=12.5e6, signals_requested = 100, card = 1):
        gr.sync_block.__init__(
            self,
            name='Save Card Signals',
            in_sig=[np.complex64],
            out_sig=[]
        )
        ## Make Variables that persistent with each loop
        self.data = []
        self.rx_fs = rx_fs
        self.tx_fs = tx_fs
        self.flagBits = ['00100100','00100101','00100110','00100111']
        self.signals_found = 0
        self.signals_requested = signals_requested
        self.tx_len = 0
        self.card = card
        self.message_port_register_in(pmt.intern("tx_len"))
        self.set_msg_handler(pmt.intern("tx_len"), self.handle_msg)
        self.message_port_register_out(pmt.intern("flagBits"))
        self.message_port_pub(pmt.intern("flagBits"), pmt.intern(self.flagBits[0]))
        self.flagBitsIndex = 0
        

        
    #Get tx_len from generate command data block
    def handle_msg(self, msg):
        self.tx_len = pmt.to_long(msg)

    def work(self, input_items, output_items):
        
        while self.flagBitsIndex < 4:    
            #Changing variables based on Data rate and subcarrier number combination
            flagBits = self.flagBits[self.flagBitsIndex]
            match flagBits[6:8]:
                case '00':
                    data_directory = Path('C:/Users/Documents/Research_Summer2024/DataCollection/GNURadio/Data/OneSubcarrierLowDataRate')
                    SOF_time = (151.04e-06) * 4
                    bit_time = (37.76e-06) * 4
                case '01':
                    data_directory = Path('C:/Users/Documents/Research_Summer2024/DataCollection/GNURadio/Data/TwoSubcarriersLowDataRate')
                    SOF_time = (149.85e-06) * 4
                    bit_time = (37.46e-06) * 4
                case '10':
                    data_directory = Path('C:/Users/Documents/Research_Summer2024/DataCollection/GNURadio/Data/OneSubcarrierHighDataRate')
                    SOF_time = 151.04e-06
                    bit_time = 37.76e-06
                case '11':
                    data_directory = Path('C:/Users/Documents/Research_Summer2024/DataCollection/GNURadio/Data/TwoSubcarriersHighDataRate')
                    SOF_time = 149.85e-06
                    bit_time = 37.46e-06

            # Define file paths
            os.makedirs(data_directory, exist_ok=True)
            card_name = 'card' + str(self.card) + '.npy'
            self.card_sig_path = data_directory / card_name
            self.corr_sig_path = data_directory / 'corr_signal.npy'

            SOF_length = round(SOF_time/(1/self.rx_fs))
            bit_length = round(bit_time/(1/self.rx_fs))
            response_bits = 8
            response_length = SOF_length + (bit_length * (response_bits))

            #Create files if they don't exist
            if not self.card_sig_path.is_file():
                np.save(self.card_sig_path,  np.zeros((0,response_length), dtype=np.complex64))

            self.corr_signal = np.load(self.corr_sig_path, allow_pickle=True)

            # Collect incoming samples
            
            # Runs when enough data is collected and stored
            if len(self.data) >= 2000000:
                
                prev_cards = np.load(self.card_sig_path, allow_pickle=True)
                self.signals_found = prev_cards.shape[0]
                buffer = np.array(self.data, dtype=np.complex64)
                try:
                    card_signals = findCardSignals(buffer, self.rx_fs, self.tx_fs, flagBits, self.tx_len) # Finds all possible card signals from collected data
                    card_signals = normalize_data(self, card_signals) # Makes sure they all have the same mean
                except:
                    self.data = []
                    return 0
                ## Removes card signals that are not similar to the correlation signal (a known card signal)
                row_to_remove = []
                for i in range(card_signals.shape[0]):
                    # diff = differences(self.corr_signal, card_signals[i])
                    diff = pearsonr(np.abs(self.corr_signal), np.abs(card_signals[i]))[0]
                    # logger.debug('Signal: ' + str(i) + ' Diff: ' + str(diff))
                    if diff < 0.8:
                        row_to_remove.append(i)
                card_signals = np.delete(card_signals, row_to_remove, axis=0)

                ## Finds how signals we still need to find
                signals_remaining = self.signals_requested - self.signals_found
                if signals_remaining > card_signals.shape[0]:
                    signals_remaining = card_signals.shape[0]
                
                ## Adds and saves newly found signals
                card_signals = np.vstack((prev_cards, card_signals[:signals_remaining]))
                self.signals_found = card_signals.shape[0]
                logger.debug("Signals Found: " + str(self.signals_found))
                np.save(self.card_sig_path, card_signals)

                ## Checks if all signals are found
                if self.signals_found >= self.signals_requested:
                    card_signals = normalize_data(self, card_signals)
                    np.save(self.card_sig_path, card_signals)
                    logger.debug("-------FLAGBITS: " + str(self.flagBits[self.flagBitsIndex]) + " COMPLETED-------")
                    self.flagBitsIndex = self.flagBitsIndex + 1
                    self.message_port_pub(pmt.intern("flagBits"), pmt.intern(self.flagBits[self.flagBitsIndex]))
                    self.data = []
                else:
                    self.data = []
                return 0
            ## Collects data
            elif len(self.data) <= 2000000:
                self.data.extend(input_items[0])
                return len(input_items[0])
            return 0
        return 0
            
def findCardSignals(data,rx_fs, tx_fs, flagBits, tx_len):
    abs_data = np.abs(data)

    ## Gets the correct timings of received data
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
    # logger.debug("finding rfreset")
    ## Finds when the received signal is Low
    start = findRFreset(data)
    data = data[start:]
    ## Loops through data to find all the card signals
    # logger.debug("into while loop")
    while ((tx_start+(2*command_length)) < len(abs_data)):
        abs_data = np.abs(data)
        # Finds when data goes high (start of command transmission)
        # logger.debug("finding when data goes high")
        for i in range(0,len(abs_data), 100):
            window_size = 100
            if (i + window_size) > (len(abs_data) - 1):
                window_size = len(abs_data) - i - 1
            delta = np.abs(abs_data[i+window_size] - abs_data[i])
            if delta > 0.1:
                tx_start = i
                break
            tx_start = None
        if (tx_start is None):
            return card_signals[1:]
        
        offset = tx_start + (command_length - slot_length - rf_reset_length) # Finds end of command transmission
        # Finds the start of the card response
        # logger.debug("finding response start")
        response_start = findResponseStart(data[offset:], N , rho)
        # if response_start == None:
        #     # Finds the next time transmission pauses
        #     # logger.debug("start not found")
        #     data = data[tx_start + command_length - rf_reset_length:]
        #     start = findRFreset(data)
        #     data = data[start:]
        #     continue
        offset = offset + response_start - SOF_low_length
        
        # Gets card signal
        card_signal = data[offset:offset + response_length]
        card_signals = np.vstack((card_signals,card_signal))
        
        # Finds the next time transmission pauses
        # logger.debug("finding next time transmission pauses")
        data = data[tx_start + command_length - rf_reset_length:]
        start = findRFreset(data)
        data = data[start:]
    return card_signals[1:]
    

def findResponseStart(data, N, rho):
    data = np.abs(data)
    delta = np.abs(np.diff(data))
    midPoint = int(np.floor(N/2) + 1)
    deltaSegment = delta[midPoint:N]
    sigma = rho * np.mean(deltaSegment)
    start = np.where(delta > sigma)[0][0]
    return start

def findRFreset(data):
    window_size = 1000
    for i in range(0, len(data), window_size):
            avg = np.mean(abs(data[i:i+window_size]))
            if avg <= 0.001:
                return i

## Uses a sliding window and mean to find how similar two arrays are           
def differences(arr1, arr2):
    windows_size = 10
    diffs = []
    for i in range(0,len(arr1)-windows_size, windows_size):
        arr1_mean = np.mean(np.abs(arr1[i:i+windows_size]))
        arr2_mean = np.mean(np.abs(arr2[i:i+windows_size]))
        diff = np.abs(arr1_mean - arr2_mean)
        diffs = np.append(diffs, diff)
    return np.mean(diffs)

## Makes the input array have the same mean as correlation signal
def normalize_data(self, data):
    data = np.asarray(data, np.complex_)
    overall_mean_magnitude = np.mean(np.abs(self.corr_signal))
    row_means = np.mean(np.abs(data), axis=1)
    normalized_data = np.empty_like(data, dtype=np.complex_)
    for i in range(data.shape[0]):
        magnitudes = np.abs(data[i])
        phases = np.angle(data[i])

        scale_factor = overall_mean_magnitude / row_means[i]

        new_magnitudes = magnitudes * scale_factor

        normalized_data[i] = new_magnitudes * np.exp(1j * phases)
    return normalized_data
    

