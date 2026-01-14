clc;

addpath("CommandGeneration\");

%% Transmission and Reception Parameters
center_frequency = 13.56e+06;
tx_fs = 12.5e+06;
InterpolationFactor = round(100e+06/tx_fs);
rx_fs = 2e+06;
DecimationFactor = round(100e+06/rx_fs);

%% Parameters/Fields for Command
ask_percent = 1;
flagBits = 0b00100110;
commandCode = 0x01;
maskLength = 0b00000000;
flagBitsStr = dec2bin(flagBits, 8);

%% Get the command data to transmit
command_data = generateCommandData(tx_fs, ask_percent, flagBits, commandCode, maskLength); % Get command data

save("command_data.mat", "command_data");