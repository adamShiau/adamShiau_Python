import matplotlib.pyplot as plt
import numpy as np

mod = 8192
mod_pol = 1
ladder_step = 2000
ramp = 0
ramp_out = 0
ramp_arr = np.empty(0)
mod_out_arr = np.empty(0)
ramp_out_pre_arr = np.empty(0)
ramp_out_arr = np.empty(0)
for i in range(70):
    ramp += ladder_step
    mod_out = mod * mod_pol
    ramp_out_pre = ramp + mod_out
    ramp_out = ramp_out_pre % 65536
    # print(i, end=', ')
    # print(ramp_out_pre_arr, end=', ')
    # print(ramp_out_arr)
    mod_pol = -mod_pol
    for j in range(10):
        ramp_arr = np.append(ramp_arr, ramp)
        mod_out_arr = np.append(mod_out_arr, mod_out)
        ramp_out_pre_arr = np.append(ramp_out_pre_arr, ramp_out_pre_arr)
        ramp_out_arr = np.append(ramp_out_arr, ramp_out)

plt.subplot(4, 1, 1)
plt.plot(mod_out_arr, label='mod')
plt.legend()
plt.subplot(4, 1, 2)
plt.plot(ramp_arr, label='ladder wave')
plt.legend()
plt.subplot(4, 1, 3)
plt.plot(ramp_out_pre_arr, label='ramp_out_Pre')
plt.axhline(y=0, color='r', linestyle='--', label='y=0')
plt.axhline(y=65536, color='r', linestyle='--', label='y=65536')
plt.axhline(y=65536*2, color='r', linestyle='--', label='y=65536*2')
plt.legend()
plt.subplot(4, 1, 4)
plt.plot(ramp_out_arr, label='ramp_out')
plt.legend()
plt.show()
