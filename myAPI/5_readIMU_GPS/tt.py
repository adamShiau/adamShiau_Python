from datetime import datetime
import time

for i in range(100):
    time.sleep(0.01)
    currentDateAndTime = datetime.now()
    MM = currentDateAndTime.month
    yy = currentDateAndTime.year
    dd = currentDateAndTime.day
    hh = currentDateAndTime.hour
    mm = currentDateAndTime.minute
    ss = currentDateAndTime.second
    us = currentDateAndTime.microsecond
    print(currentDateAndTime)
    print(yy)
    print(MM)
    print(dd)
    print(hh)
    print(mm)
    print(ss + us*1e-6)
    # print(ss2)
    print(time.time())

