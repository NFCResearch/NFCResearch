function  data = modulateCommand(command, tx_fs, ask_percent)

    %% Convert hex string command to binary values
    dec = hex2dec(command);
    binaryCommand = dec2bin(dec, length(command) * 4);
    %% Get the number of samples for a pair of bits
    pair_samples = round((75.52e-06)/(1/tx_fs));
    %% Create array for when transmission goes low
    low_percent = 1-ask_percent;
    low_samples = round((9.44e-06)/(1/tx_fs));
    low_data = ones(low_samples, 1) * low_percent;

    %% Loop through pairs of binary values creating an array depending on
    % on the pair, then appending the pair on the data array
    data = [];
    for i=1:2:length(binaryCommand)
        pair = binaryCommand(i:i+1);
        pair_data = ones(pair_samples, 1);
        switch pair
            case "00"
                high_samples = round((9.44e-06)/(1/tx_fs));
                pair_data(high_samples:high_samples + low_samples  - 1) = low_data;
            case "01"
                high_samples = round((28.32e-06)/(1/tx_fs));
                pair_data(high_samples:high_samples + low_samples  - 1) = low_data;
            case "10"
                high_samples = round((47.2e-06)/(1/tx_fs));
                pair_data(high_samples:high_samples + low_samples  - 1) = low_data;
            case "11"
                high_samples = round((66.08e-06)/(1/tx_fs));
                pair_data(high_samples:high_samples + low_samples  - 1) = low_data;
        end
        data = [data; pair_data];
    end
end