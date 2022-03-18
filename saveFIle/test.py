import numpy as np

file=open('tt.txt', 'w')
file.writelines(['1\n', '2\n', '3\n'])
file.close()

f = np.loadtxt('tt.txt')
print('f before: ', f)
f[1] = 100

file=open('tt.txt', 'w')
# print(f.shape)
# print(f)
# print(f[1])


np.savetxt(file, f)
file.close()