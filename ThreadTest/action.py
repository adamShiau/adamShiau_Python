from PyQt5.QtCore import *
import time
import sys

LOOPDELAY = sys.float_info.min

class action2(QThread):
	"""
	Runs a counter thread.
	"""
	run_flag = 0
	cnt = 0
	act_signal = pyqtSignal(int)

	def run(self):
		if(self.run_flag):
			while(self.run_flag):
				self.cnt = self.cnt + 1
				self.act_signal.emit(self.cnt)
				time.sleep(LOOPDELAY)
				print(LOOPDELAY)
		else:
			print('run_flag = ', self.run_flag)



class action(QObject):
	run_flag = 0
	cnt = 0
	act_signal = pyqtSignal(int)
	def __init__(self):
		super().__init__()
		print('hello');
		# self.doLoop()
		
	def doLoop(self):
		if(self.run_flag):
			while(self.run_flag):
				self.cnt = self.cnt + 1
				self.act_signal.emit(self.cnt)
				time.sleep(1)
		else:
			print('run_flag = ', self.run_flag)