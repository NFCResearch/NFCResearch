function card_signals = findCardSignal(data, rx_fs, tx_fs, flagBits, command)
    rate_flag = flagBits(7);
    %% Get the Slot Length
    
    % High Data Rate Slot Length
    if (rate_flag == '1')
        slot_length = round(8160e-06/(1/rx_fs));
    else
    % Low Data Rate Slot
        slot_length = round(20332e-06/(1/rx_fs));
    end
    
    %% Level out Data
    agc = comm.AGC( "DesiredOutputPower",1, ...
                    "AveragingLength",100);
    
    agc_data = agc(data);
    
    rf_reset_length = round(8160e-06/(1/rx_fs));
    command_time = length(command) / tx_fs;
    command_length = round((command_time/(1/rx_fs)) + (2.5e-04/(1/rx_fs)));
    
    N = 50;
    rho = 5;
    
    %Get the time of response
    switch flagBits(7:8)
        %Low Data Rate, One Subcarrier
        case '00'
            SOF_time = (151.04e-06) * 4;
            SOF_low_time = (56.64e-06) * 4;
            bit_time = (37.76e-06) * 4;
        %Low Data Rate, Two Subcarriers
        case '01'
            SOF_time = (149.85e-06) * 4;
            SOF_low_time = 0;
            bit_time = (37.46e-06) * 4;
        %High Data Rate, One Subcarrier
        case '10'
            SOF_time = 151.04e-06;
            SOF_low_time = 56.64e-06;
            bit_time = 37.76e-06;
        %High Data Rate, Two Subcarriers
        case '11'
            SOF_time = 149.85e-06;
            SOF_low_time = 0;
            bit_time = 37.46e-06;
    end
    
    SOF_length = round(SOF_time/(1/rx_fs));
    SOF_low_length = round(SOF_low_time/(1/rx_fs));
    bit_length = round(bit_time/(1/rx_fs));
    response_bits = 8;
    response_length = SOF_length + (bit_length * (response_bits));
    peak = 0;
    card_signals = [];
    
    while (peak+(2*command_length)) < length(agc_data)
        % Find the start of command transmission
        for i=1:length(agc_data)
            if (abs(agc_data(i)) > 20)
                peak = i;
                break;
            end
        end
        % Get the time of transmission
        offset = peak + (command_length - slot_length - rf_reset_length);
        
        % Find start of response
        response_start = findResponseStart(abs(agc_data(offset:end)), N, rho);
        offset = offset + response_start -SOF_low_length;
        
        card_signal = agc_data(offset:offset + response_length);
        card_signals = [card_signals, card_signal];
        agc_data(1:peak + command_length - rf_reset_length) = 0;
    end
end


function start = findResponseStart(signal, N, rho)
    delta = abs(diff(signal));
    midPoint = floor(N / 2) + 1;
    deltaSegment = delta(midPoint:N);
    sigma = rho * mean(deltaSegment);
    start = find(delta > sigma, 1);
end
