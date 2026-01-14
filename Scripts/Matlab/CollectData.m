clc

addpath("CommandGeneration\");
addpath("Data\");

%% Transmission and Reception Parameters
center_frequency = 13.56e+06;
tx_fs = 12.5e+06;
InterpolationFactor = round(100e+06/tx_fs);
rx_fs = 2e+06;
DecimationFactor = round(100e+06/rx_fs);

%% Parameters/Fields for Command
ask_percent = 1;
flagCombinations = [0b00100100, 0b00100101, 0b00100110, 0b00100111];
flagBits = 0b00100101;
commandCode = 0x01;
maskLength = 0b00000000;

%% Save Parameters
Card = 1; % Change to what card is being used
num_of_trials = 300;
for flagBits = flagCombinations
    %% set up receiving radio
    rx = comm.SDRuReceiver(...
        Platform = "N200/N210/USRP2", ...
        OutputDataType = "double", ...
        DecimationFactor = DecimationFactor, ...
        CenterFrequency = center_frequency, ...
        Gain=0, ...
        SamplesPerFrame = 100000);
    
    %% set up transmitter radio
    tx = comm.SDRuTransmitter(Platform = 'N200/N210/USRP2', ...
        CenterFrequency = center_frequency, ...
        Gain=0, ...
        InterpolationFactor = InterpolationFactor);
    
    flagBitsStr = dec2bin(flagBits, 8);
    
    %% Get the correct test card signal for correlation coeffiecent
    switch flagBitsStr(7:8)
        %Low Data Rate, One Subcarrier
        case '00'
            load(".\Data\OneSubcarrierLowDataRate\test_card_signal.mat");
            folder = strcat(".\Data\OneSubcarrierLowDataRate\Card", int2str(Card), ".mat"); % Change card number
            disp("Started Collecting for One Subcarrier Low Data Rate");
        %Low Data Rate, Two Subcarriers
        case '01'
            load(".\Data\TwoSubcarriersLowDataRate\test_card_signal.mat");
            folder = strcat(".\Data\TwoSubcarriersLowDataRate\Card", int2str(Card), ".mat"); % Change card number
            disp("Started Collecting for Two Subcarriers Low Data Rate");
        %High Data Rate, One Subcarrier
        case '10'
            load(".\Data\OneSubcarrierHighDataRate\test_card_signal.mat");
            folder = strcat(".\Data\OneSubcarrierHighDataRate\Card", int2str(Card), ".mat"); % Change card number
            disp("Started Collecting for One Subcarrier High Data Rate");
        %High Data Rate, Two Subcarriers
        case '11'
            load(".\Data\TwoSubcarriersHighDataRate\test_card_signal.mat");
            folder = strcat(".\Data\TwoSubcarriersHighDataRate\Card", int2str(Card), ".mat"); % Change card number
            disp("Started Collecting for Two Subcarriers High Data Rate");
    end
    
    %% Get the command data to transmit
    command_data = generateCommandData(tx_fs, ask_percent, flagBits, commandCode, maskLength); % Get command data
    
    %% Collect Data until end trial number is reached
    trials_complete = 0;
    card_signals = [];
    while trials_complete < num_of_trials
    
        rx_data = []; % initialize rx_data array
    
        %% transmits and receives data
       
        disp("Transmitting and Receiving...")
        for i = 1:100
            try
                step(tx,command_data);
            catch ME
                if (strcmp(ME.identifier, "sdru:SDRuTransmitter:TransmitUnsuccessful"))
                    cprintf('red', "Underrun detected\n")
                    continue;
                elseif (strcmp(ME.identifier, "sdru:SDRuBase:InvalidIPAddress"))
                    cprintf('red', "Invalid IPaddress, retrying...\n")
                    release(rx)
                    release(tx ...
                        )
                    continue;
                else
                    rethrow(ME)
                end
            end
            data_frame = step(rx);
            rx_data = [rx_data; data_frame];
        end
        try
        disp("Finding Card Signals...");
        new_card_signals = findCardSignal(rx_data, rx_fs, tx_fs, flagBitsStr, command_data);
        cols_to_remove = [];
        for col = 1:size(new_card_signals,2)
            correlation = abs((corrcoef(test_card_signal, new_card_signals(:,col))));
            if (correlation(1,2) < 0.999)
                cols_to_remove = [cols_to_remove, col];   
            end
        end
        catch err
            cprintf('red', "Card Signal Not Found retrying...\n");
            release(rx);
            release(tx);
            continue;
        end
       
        new_card_signals(:, cols_to_remove) = [];
        trials_remaining = num_of_trials - trials_complete;
        if trials_remaining > size(new_card_signals,2)
            trials_remaining = size(new_card_signals,2);
        end
        card_signals = [card_signals, new_card_signals(:,1:trials_remaining)];
        trials_complete = size(card_signals,2);
        
        disp("Found:"+ int2str(trials_complete));
        release(rx);
        release(tx);
    end
    
    save(folder, "card_signals");    
    clearData();
end

cprintf('green', "Done.\n");

%% Releases
release(rx)
release(tx)

function clearData()
    clear rx;
    clear tx;
    clear command_data;
    clear trial_complete;
    clear card_signals;
    clear new_card_signals;
    clear cols_to_remove;
    clear rx_data;
    clear data_frame;
    clear ME;
    clear correlation;
    clear folder;
    clear trials_remaining;
end