import numpy as np

num_cards = 52
num_trials = 500
OneHigh_ = np.zeros((num_trials,910,num_cards), dtype=complex)
OneLow_ = np.zeros((num_trials,3624,num_cards), dtype=complex)
TwoHigh_ = np.zeros((num_trials,900,num_cards), dtype=complex)
TwoLow_ = np.zeros((num_trials,3599,num_cards), dtype=complex)

data_arrays = [OneHigh_, OneLow_, TwoHigh_, TwoLow_]
data_variations = ["OneHigh_", "OneLow_", "TwoHigh_", "TwoLow_"]
data_variations_len = [910,3624,900,3599]

for combo in range(4):
    for card in range(num_cards):
        card_path = '../GNURadio/Data/' + data_variations[combo] + "/card" + str(card + 1) + ".npy"
        card_array = np.load(card_path, allow_pickle=True)
        data_arrays[combo][:,:,card] = card_array
    np.save( '../GNURadio/Data/' + data_variations[combo] +'.npy', data_arrays[combo])
    print(data_arrays[combo].shape)