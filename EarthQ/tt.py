import os
import time 
import datetime
import numpy as np

dirname = os.path.dirname(__file__) #get path of current file 
# print(dirname)
dataPath = os.path.join(dirname, 'data') #enter the directory name to save data
# print(dataPath)

''' 
autoCreateDir: 檢查給定路徑資料夾是否存在，若無則建立資料夾，若有則不做任何事
輸入:
dataPath : 資料夾之絕對路徑
dirName : 資料夾名稱
busy: 若為1則不做任何事
輸出: 
status: 	0.=不存在資料夾，建立資料夾成功
			1.=已存在資料夾，不建立新資料夾
			2.=目前狀態為busy，不做任何事
filepath: 輸出資料夾絕對路徑

'''
def autoCreateDir(dataPath, dirName, busy):
	filepath = os.path.join(dataPath, str(dirName))
	if not busy:
		folder_exist = os.path.exists(filepath)
		if not folder_exist:
			print('\ncreate folder: ', filepath)
			os.mkdir(filepath)
			status = 0
		else:
			print('\nfolder exist!')
			status = 1
	else:
		status = 2
	return status, filepath
''' 
open_and_save_data: 輸入計數器與最大資料數量，
'''
def open_and_save_data(data_ptr, max_dataNum, rst_n, filePath, idx, data1, data2):
	print('in_data_ptr: ', data_ptr)
	# print('in_ busy: ', busy)
	print('in_ idx: ', idx)
	if(data_ptr == max_dataNum): 
		f=open(os.path.join(filePath, str(idx)) +'.txt', 'w')
		f.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
		np.savetxt(f, np.vstack([data1, data2]).T, fmt='%d, %d')
		busy = 1
		status = 0
		f.close
	elif(data_ptr == 1 or rst_n == 0):
		np.savetxt(f, np.vstack([data1, data2]).T, fmt='%d, %d')
		f.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
		f.close
		busy = 0
		status = 1
	else:
		np.savetxt(f, np.vstack([data1, data2]).T, fmt='%d, %d')
		busy = 1
		status = 2
	return status, busy
	
if __name__ == '__main__':
	#initialization
	max_dataNum = 10
	g_busy = 0
	g_data_ptr = max_dataNum
	rst_n = 1 #self.run_flag
	g_idx = 1
	print('current path: ', dirname)
	for i in range(1, 50):
		
		status, filepath1 = autoCreateDir(dataPath,  datetime.datetime.now().year,  g_busy)
		status, filepath2 = autoCreateDir(filepath1, datetime.datetime.now().month, g_busy)
		print('i= ', i, end='\t')
		print('g_busy= ', g_busy, end='\t')
		print('status= ', status, end='\t')
		print('g_data_ptr= ', g_data_ptr, end='\t')
		print('rst_n= ', rst_n, end='\t')
		print('g_idx= ', g_idx)
		aa, g_busy = open_and_save_data(g_data_ptr, max_dataNum, rst_n, filepath2, g_idx, 456, 123)
		if(status == 0):
			g_idx = 0 #如果建立新資料夾，重製檔案名稱_idx
		if(rst_n):
			g_idx = g_idx + 1
		if(g_data_ptr == 1):#資料數量指標=1時代表關閉檔案了，此時重制至max_dataNum
			g_data_ptr = max_dataNum
		g_data_ptr = g_data_ptr - 1
		if(i==50):
			rst_n = 0
		if(i==60):
			rst_n = 1
	
	# print('status1: ', status1)
	# print('filepath1: ', filepath1)
	# print('status2: ', status2)
	# print('filepath2: ', filepath2)
	
