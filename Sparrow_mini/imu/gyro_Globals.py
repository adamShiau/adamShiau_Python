global kal_status
global kal_Q
global kal_R
global PRINT_MODE
global TEST_MODE
global OP_MODE
MODE_FOG			= 1
MODE_IMU			= 2
MODE_EQ				= 3
MODE_IMU_FAKE		= 4

kal_status = 0
kal_Q = 1
kal_R = 10
PRINT_MODE = 1 #1 : print mode; 0: plot mode
TEST_MODE = 0
OP_MODE = MODE_IMU_FAKE