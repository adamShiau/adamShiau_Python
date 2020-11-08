import os
import numpy as np 
import struct
import logging

def unsignedToSigned(usInput, maxbit):
	mask = 2**(maxbit)-1
	signedMax = 2**(maxbit -1)-1
	if usInput > signedMax:
		usInput = ((~(usInput-1))&mask)
		usInput = usInput*(-1)
	return usInput


def ArraytoBinFile(fname, array1D, packtype):
	fp = open(fname,'wb')
	for value in array1D:
		data = struct.pack(packtype, value)
		fp.write(data)
	fp.close()


def BinFiletoArray(fname, bytes, unpacktype, loggername):
	output = np.empty(0)
	logger = logging.getLogger(loggername)
	if os.path.exists(fname) == False:
		logger.error("Bin file doesn't exists")
	else:
		fp = open(fname,"rb")
		try:
			data = fp.read(bytes)
			while data != "":
				temp = struct.unpack(unpacktype, data)
				output = np.append(output, temp[0])
				data = fp.read(bytes)
		# except:
		# 	logger.error("file read error")	
		# else:
		# 	pass
		finally:
			fp.close()
			return output

def BinFiletoArray2(fname, bytes, unpacktype, loggername):
	output = np.empty(0)
	logger = logging.getLogger(loggername)
	if os.path.exists(fname) == False:
		logger.error("Bin file doesn't exists")
	else:
		fp = open(fname,"rb")
		try:
			data = fp.read(bytes)
			while len(data) == 4:
				temp = struct.unpack(unpacktype, data)
				output = np.append(output, temp[0])
				# print(output)
				data = fp.read(bytes)
		# except:
		# 	logger.error("file read error")	
		# else:
		# 	pass
		finally:
			# print("file len = " + str(len(output)))
			fp.close()
			return output

def TexTFileto1DList(fname, loggername):
	logger = logging.getLogger(loggername)
	if os.path.exists(fname):
		fp = open(fname)
		outlist = [line.rstrip('\n') for line in fp] 
		fp.close()
		return outlist
	else:
		logger.warning("Text file doesn't exists")
		return []

def TexTFileto2DList(fname, spliter, loggername, headerLine = 0):
	num = 0
	logger = logging.getLogger(loggername)
	if os.path.exists(fname):
		outlist = []
		fp = open(fname)
		for line in fp:
			num += 1
			subline = line.rstrip('\n')
			if (num > headerLine):
				outlist.append(subline.split(spliter))
				#print(subline.split(spliter))
		fp.close()
		return outlist
	else:
		logger.warning("Text file doesn't exists")
		return []

def TexTFileto1DArray(fname, loggername):
	data = np.empty(0)
	logger = logging.getLogger(loggername)
	if os.path.exists(fname):
		fp = open(fname)
		outlist = [line.rstrip('\n') for line in fp] 
		for a in outlist:
			data = np.append(data, float(a))
		fp.close()
	else:
		logger.warning("Text file doesn't exists")
	return data

def TexTFileto2ColumeArray(fname, spliter, loggername, headerLine):
	out = TexTFileto2DList(fname, spliter, loggername, headerLine)
	data0 = np.zeros(0)
	data1 = np.zeros(0)
	index = len(out)
	for i in range(0, index):
		data0 = np.append(data0, float(out[i][0]))
		data1 = np.append(data1, float(out[i][1]))
	return data0, data1

def TexTFileto3ColumeArray(fname, spliter, loggername, headerLine):
	out = TexTFileto2DList(fname, spliter, loggername, headerLine)
	data0 = []
	data1 = np.zeros(0)
	data2 = np.zeros(0)
	index = len(out)
	for i in range(0, index):
		data0 = np.append(data0, out[i][0])
		data1 = np.append(data1, float(out[i][1]))
		data2 = np.append(data2, float(out[i][2]))
	return data0, data1, data2

def array1DtoTextFile(fname, array, loggername, header = ""):
	logger = logging.getLogger(loggername)
	fp = open(fname,"w")
	if header != "":
		header = header + "\n"
		fp.writelines(header)
	
	if len(array) == 0:
		logger.error("array is empty")
	else:
		for data in array:
			fp.write(str(data) + '\n')
		fp.close()

def list2DtoTextFile(fname, list2d, spliter, loggername, header = "", double_float = False):
	logger = logging.getLogger(loggername)
	fp = open(fname,"w")
	if header != "":
		header = header + "\n"
		fp.writelines(header)

	if len(list2d) == 0:
		logger.error("array is empty")

	for list1d in list2d:
		for element in list1d:
			if ( (type(element) == float) \
			or (type(element) == np.float64) ) :
				if (double_float):
					fp.write("%3.8f"%element+spliter+" ")
				else:
					fp.write("%3.4f"%element+spliter+" ")
			else:
				fp.write(str(element)+spliter+" ")
		fp.write("\n")
	fp.close()


if __name__ == '__main__':
	unsignedToSigned(255, 8)
