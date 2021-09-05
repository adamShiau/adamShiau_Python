import os
import time 
import datetime
import numpy as np
f=open('test.txt', 'w', buffering=1)
for i in range(10000):
	
	np.savetxt(f, np.vstack([i, 2]).T, fmt='%d, %d')
	time.sleep(0.1)
f.close()