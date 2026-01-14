function data = modulateSOF_EOF(data, tx_fs, ask_percent)

    %% Get length of SOF and EOF
    SOF_length = round((75.52e-06)/(1/tx_fs));
    EOF_length = round(SOF_length/2);
    
    %% Create array for when transmission goes low
    low_percent = 1-ask_percent;
    low_samples = round((9.44e-06)/(1/tx_fs));
    low_data = ones(low_samples, 1) * low_percent;

    %% Generate SOF
    SOF = ones(SOF_length, 1);
    SOF(2:2 + low_samples -1) = low_data;
    high_samples = round((47.2e-06)/(1/tx_fs));
    SOF(high_samples:high_samples + low_samples  - 1) = low_data;

    %% Generate EOF
    EOF = ones(EOF_length, 1);
    high_samples = round((18.88e-06)/(1/tx_fs));
    EOF(high_samples:high_samples + low_samples  - 1) = low_data;

    %% Add to data
    data = [SOF;data;EOF];
end