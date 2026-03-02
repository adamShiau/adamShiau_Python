import serial

ser = serial.Serial('COM18', baudrate=230400)
ser.write(bytearray([0xAB, 0xBA]))
ser.write([0x66, 0, 0, 0, 0x05, 0x02])
ser.write(bytearray([0x55, 0x56]))
line = ser.readline()
print(line)
print(line.decode('utf-8'))