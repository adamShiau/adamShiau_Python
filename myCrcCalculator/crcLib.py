def crc_8(message, nBytes):
    """
    Description
    -----------
    Calculate 8-bit CRC of input message.
    ref: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
    Parameters
    ----------
    message: byte list, to be used to calculate the CRC.
    nBytes: int, total bytes number of input message.
    Returns
    -------
    remainder: One byte CRC value.
    """
    WIDTH = 8
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x07
    remainder = 0
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))

        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)
    return remainder


def crc_32(message, nBytes):
    WIDTH = 32
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x04C11DB7
    remainder = 0xFFFFFFFF
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))
        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFFFFFFFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)
    return [remainder >> 24 & 0xFF, remainder >> 16 & 0xFF, remainder >> 8 & 0xFF, remainder & 0xFF]


if __name__ == "__main__":
    # data1 = [0xFE, 0x81, 0xFF, 0x55, 0xBC, 0x64, 0x6C, 0x1E]
    # data2 = [0x3C, 0x3F, 0xF9, 0x81, 0x3B, 0x3C, 0x1E, 0x78]
    # data3 = [0xBC, 0x06, 0x5F, 0xB7, 0xBB, 0x2F, 0xBD, 0x79]
    # data4 = [0x3F, 0x7E, 0x98, 0x00, 0x77, 0x47, 0x00, 0x14]
    data1 = [0xFE, 0x81, 0xFF, 0x55, 0x00, 0x00, 0x00, 0x00]
    data2 = [0x00, 0x00, 0x00, 0x00, 0x00, 0xC4, 0x00, 0x25]
    data3 = [0xFD, 0x85, 0xFF, 0xBB, 0x00, 0x1B, 0xE3, 0x04]
    data4 = [0x0E]
    data = data1 + data2 + data3 + data4
    # print([hex(i) for i in data])
    # print(len(data))
    print("%x\n" % crc_8(data, len(data)))
    # print("%x\n" % crc_32(data, len(data)))
    print([hex(i) for i in crc_32(data, len(data))])
