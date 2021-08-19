import os
import time 
import datetime
import numpy as np

dirname = os.path.dirname(__file__) #get path of current file 
# print(dirname)
dataPath = os.path.join(dirname, 'data') #enter the directory name to save data
# print(dataPath)

def autoCreateDir(dataPath, dirName):
	filepath = os.path.join(dataPath, str(dirName))
	folder_exist = os.path.exists(filepath)
	if not folder_exist:
		print('\ncreate folder: ', filepath)
		os.mkdir(filepath)
		success = 1
	else:
		print('\nfolder exist!')
		success = 0
	return success, filepath
	
def open_and_save_data(cnt, dataNum, filePath, data1, data2, idx):
	if(cnt==dataNum): 
		f=open(os.path.join(filePath, str(idx)) +'.txt', 'w')
		f.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
		status = 1
	elif(cnt==1):
		f.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
		f.close
		status = 0
	else:
		np.savetxt(f, np.vstack([data1, data2]).T, fmt='%d, %d')
		status = 2
	return status
	
if __name__ == '__main__':
	print('current path: ', dirname)
	flag1, filepath1 = autoCreateDir(dataPath,  datetime.datetime.now().year)
	flag2, filepath2 = autoCreateDir(filepath1, datetime.datetime.now().month)
	print('flag1: ', flag1)
	print('filepath1: ', filepath1)
	print('flag2: ', flag2)
	print('filepath2: ', filepath2)
	
	# f=open(os.path.join(filepath2, str(0)) + '.txt', 'a')
	# np.savetxt(f, np.array([456]), fmt='%d')
	# f.close
	
	cnt = 100
	dataNum = 100
	data1 = 11
	data2 = 12
	idx = 0
	
	for i in range(1,500):
		status = open_and_save_data(cnt, dataNum, filepath2, data1, data2, idx)
		if(cnt == 1):
			cnt = 100
		else:
			cnt = cnt - 1
		if(status == 0):
			idx = idx + 1