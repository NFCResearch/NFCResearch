function  data = generateResetToReady(tx_fs, flagBits,ask_percent)

    flagBits = strcat('000000', flagBits(7:8));
    flagBits = bin2dec(flagBits);
    

    commandCode = 0x26;
    CRC = calculateCRC([flagBits, commandCode]);
    commandCode = dec2bin(commandCode,8);
    flagBits = dec2bin(flagBits,8);
    
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
    
    rearranged_CRC = '';
    for i=length(CRC):-2:1
        bitpair = CRC(i-1:i);
        rearranged_CRC = [rearranged_CRC, bitpair];
    end

    % Prepare command string for modulation
    command = [rearranged_flagBits, rearranged_commandCode, rearranged_CRC];
    command = bin2dec(command);   % Convert binary string to decimal
    command = dec2hex(command, 8);

    %% Modulates data
    data = modulateCommand(command, tx_fs, ask_percent);
    data = modulateSOF_EOF(data, tx_fs, ask_percent);
    data = modulateSlotData(data, tx_fs, ask_percent, flagBits);
end

