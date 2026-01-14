function data = modulateSlotData(data,tx_fs, ask_percent, flagBits)

    slot_flag = flagBits(3);
    rate_flag = flagBits(7);
    inv_flag = flagBits(6);
    
    %% Create array for when transmission goes low
    low_percent = 1-ask_percent;
    low_samples = round((9.44e-06)/(1/tx_fs));
    low_data = ones(low_samples, 1) * low_percent;
    
    %% Generate EOF
    EOF_length = round((37.76e-06)/(1/tx_fs));
    EOF = ones(EOF_length, 1);
    high_samples = round((18.88e-06)/(1/tx_fs));
    EOF(high_samples:high_samples + low_samples  - 1) = low_data;

    %% Generate Slot
    % High Data Rate Slot Length
    if (rate_flag == '1')
        slot_length = round(8160e-06/(1/tx_fs));
    else
    % Low Data Rate Slot
        slot_length = round(20332e-06/(1/tx_fs));
    end
    
    slot = ones(slot_length,1);
    data = [slot; data];
    if (slot_flag == '0' && inv_flag == '1')
        % 16 Slots
        slot = [slot;EOF];
        for i=1:1:16
            data = [data; slot];
        end
    else
        % 1 slot
        data = [data; ones(slot_length, 1)];
    end
end