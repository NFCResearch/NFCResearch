function crc_value = calculateCRC(data_bytes)
    % Constants
    POLYNOMIAL = hex2dec('8408'); % x^16 + x^12 + x^5 + 1
    PRESET_VALUE = hex2dec('FFFF');
    NUMBER_OF_BYTES = length(data_bytes); % Example: 4 data bytes
    current_crc_value = PRESET_VALUE;

    for i=1:1:NUMBER_OF_BYTES
        current_crc_value = bitxor(current_crc_value, uint16(data_bytes(i)));
        for j=1:1:8
            if (bitand(current_crc_value, 0x0001))
                current_crc_value = bitxor(bitshift(current_crc_value,-1), POLYNOMIAL);
            else
                current_crc_value = bitshift(current_crc_value, -1);
            end
        end
    end
    current_crc_value = bitcmp(current_crc_value);
    crc_value = current_crc_value;
    crc_value = dec2bin(crc_value, 16);
end