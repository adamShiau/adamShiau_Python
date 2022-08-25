from datetime import datetime
import time

for i in range(100):
    time.sleep(0.5)
    currentDateAndTime = datetime.now()
    MM = currentDateAndTime.month
    yy = currentDateAndTime.year
    dd = currentDateAndTime.day
    hh = currentDateAndTime.hour
    mm = currentDateAndTime.minute
    ss = currentDateAndTime.second
    # ss = currentDateAndTime.second + currentDateAndTime.microsecond*1e-6
    print(currentDateAndTime)
    print(yy, type(yy))
    print(MM)
    print(dd)
    print(hh)
    print(mm)
    print(ss, type(ss))
    # print(ss2)
    print(time.time())

