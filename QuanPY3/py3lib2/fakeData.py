import numpy as np 
import matplotlib.pyplot as plt 

class QSS005MSData():
	def __init__(self, pts):
		self.pts = pts
		self.data = np.zeros(pts)

	def genRandDefine(self, numPeak, maxAmp):
		define = []
		for i in range(numPeak):
			pos = int(np.random.rand()*float(self.pts))
			amp = float(maxAmp)*np.random.rand()
			define.append([pos, amp])
		return define

	def genPeak(self, define, width):
		for i in range(len(define)):
			pos = define[i][0]
			amp = define[i][1]
			for j in range(width):
				if j == 0:
					self.data[pos] = self.data[pos]+ amp
				else:
					if pos+j < self.pts:
						self.data[pos+j] = self.data[pos]+ amp/(j+0.5)
					if pos-j >=0:
						self.data[pos-j] = self.data[pos-j] + amp/(j+0.5)

	def genNoise(self, noiseAmp):
			self.data = self.data + np.random.rand(self.pts)*noiseAmp 

if __name__ == '__main__':
	fakeD = QSS005MSData(200)
	define = fakeD.genRandDefine(5, 6)
	fakeD.genPeak(define, 4)
	fakeD.genNoise(1)
	plt.plot(fakeD.data)
	plt.show()

