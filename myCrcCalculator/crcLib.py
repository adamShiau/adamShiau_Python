def crcSlow(message, nBytes):
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
    byte = 0
    bit = 8
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))

        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)
    return remainder


if __name__ == "__main__":
    print("%x\n" % crcSlow([0xfe, 0x8e, 0xff, 0x55], 4))
