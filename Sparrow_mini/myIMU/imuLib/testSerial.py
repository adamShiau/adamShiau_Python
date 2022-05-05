import serial
import time
import numpy

temp_data = []
time_start = time.perf_counter()
ser = serial.Serial('COM15', 230400, timeout=0, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS,
                    stopbits=serial.STOPBITS_ONE)
# ser.reset_input_buffer()
while (time.perf_counter() - time_start) < 2:
    while ser.in_waiting < 100 :
        pass
    data_in = ser.read(10)
    data_in_str = str(data_in)
    for i in data_in:
        temp_data.append(hex(i).strip("0x"))
    print(temp_data)
    tt = ''.join(str(e) for e in temp_data)
    print(tt)
    print(data_in_str)
    print()
    temp_data=[]
ser.close()