function [data, len] = generateCommandData(tx_fs, ask_percent, flagBits, commandCode, maskLength)

    rf_reset_length = round(8160e-06/(1/tx_fs));
    CRC = calculateCRC([flagBits, commandCode, maskLength]);
    disp(CRC)
    commandCode = dec2bin(commandCode,8);
    flagBits = dec2bin(flagBits,8);
    maskLength = dec2bin(maskLength, 8);
    
    %% Rearrange Data for transmission
    rearranged_flagBits = '';
    for i=length(flagBits):-2:1
        bitpair = flagBits(i-1:i);
        rearranged_flagBits = [rearranged_flagBits, bitpair];
    end

    rearranged_commandCode = '';
    for i=length(commandCode):-2:1
        bitpair = commandCode(i-1:i);
        rearranged_commandCode = [rearranged_commandCode, bitpair];
    end
    
    rearranged_maskLength = '';
    for i=length(maskLength):-2:1
        bitpair = maskLength(i-1:i);
        rearranged_maskLength = [rearranged_maskLength, bitpair];
    end
    
    rearranged_CRC = '';
    for i=length(CRC):-2:1
        bitpair = CRC(i-1:i);
        rearranged_CRC = [rearranged_CRC, bitpair];
    end
    
    % Prepare command string for modulation
    command = [rearranged_flagBits, rearranged_commandCode, rearranged_maskLength, rearranged_CRC];
    command = bin2dec(command);
    command = dec2hex(command, 8);

    %% Modulates data
    data = modulateCommand(command, tx_fs, ask_percent);
    data = modulateSOF_EOF(data, tx_fs, ask_percent);
    
    data = modulateSlotData(data, tx_fs, ask_percent, flagBits);
    

    % Add Reset To Ready Command before desired command
    reset_data = generateResetToReady(tx_fs, flagBits, ask_percent);
    % data = [reset_data; data];
    len = length(data);
    data = [data; zeros(rf_reset_length,1)]; %Add RF Reset after command
    
    data = addSineWave(data, tx_fs, 166.66); %Embed Signal in Sine Wave
    disp(size(data))
end
