# common function

此 module 定義常用到的 methods

- [common function](#common-function)
  - [dictOperation](#dictoperation)
    - ["ADD"](#add)
    - ["SUB"](#sub)
    - ["APPEND"](#append)
  - [file_manager](#file_manager)
    - [使用](#使用)
  - [saveData2File](#savedata2file)
    - [使用](#使用-1)

## dictOperation

```python
def dictOperation(dictA: dict, dictB: dict, mode: str):

mode: str = "ADD" or "SUB" or "APPEND"

```

imudata dictionary 運算，imudata之結構為:

IMU_DATA_STRUCTURE =
{
    "NANO33_W": (wx, wy, wz),
    "NANO33_A": (ax, ay, az),
    "ADXL_A": (ax, ay, az),
    "TIME": (t,)
}

目前使用到的場景:

### "ADD"

1. 計算immudata offset值時會連續取data, 累加後取平均值

```python
#根據IMU_DATA_STRUCTURE宣告imuoffset之結構，讓個element為0
imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE[k])) for k in set(IMU_DATA_STRUCTURE)}
print(imuoffset)
data = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
for i in range(10):
    imuoffset = dictOperation(imuoffset, data, "ADD")
print(imuoffset)

imuoffset = {k: imuoffset[k]/10 for k in imuoffset}
print(imuoffset)

```

results:

```python
{'NANO33_W': array([0., 0., 0.]), 'NANO33_A': array([0., 0., 0.]), 'TIME': array([0.]), 'ADXL_A': array([0., 0., 0.])}
{'NANO33_W': array([10., 20., 30.]), 'NANO33_A': array([-10., -20., -30.]), 'TIME': array([15.]), 'ADXL_A': array([40., 50., 60.])}
{'NANO33_W': array([1., 2., 3.]), 'NANO33_A': array([-1., -2., -3.]), 'TIME': array([1.5]), 'ADXL_A': array([4., 5., 6.])}
```

2. 計算整體imudata加上一個offset值

```python
imudata = {
    "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "TIME": (np.array([1.5, 1.6, 1.7]))
}
print(imudata)
offset = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
imudata_add_offset = dictOperation(imudata, offset, "ADD")
print(imudata_add_offset)
```

results:

```python
{'NANO33_W': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'NANO33_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'ADXL_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'TIME': array([1.5, 1.6, 1.7])}
{'NANO33_W': array([[ 2,  3,  4],
                    [ 6,  7,  8],
                    [10, 11, 12]]), 
'NANO33_A': array([[0, 1, 2],
                   [2, 3, 4],
                   [4, 5, 6]]), 
'ADXL_A': array([[ 5,  6,  7],
                 [ 9, 10, 11],
                 [13, 14, 15]]), 
'TIME': array([3. , 3.1, 3.2])}
```

### "SUB"

計算整體imudata加上一個offset值

```python
imudata = {
    "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "TIME": (np.array([1.5, 1.6, 1.7]))
}
print(imudata)
offset = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
imudata_add_offset = dictOperation(imudata, offset, "SUB")
print(imudata_add_offset)
```

results:

```python
{'NANO33_W': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'NANO33_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'ADXL_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'TIME': array([1.5, 1.6, 1.7])}
{'NANO33_W': array([[0, 1, 2],
                    [2, 3, 4],
                    [4, 5, 6]]), 
'NANO33_A': array([[ 2,  3,  4],
                   [ 6,  7,  8],
                   [10, 11, 12]]), 
'ADXL_A': array([[-3, -2, -1],
                 [-1,  0,  1],
                 [ 1,  2,  3]]), 
'TIME': array([0. , 0.1, 0.2])}
```

### "APPEND"

1. 在memsImuReader裡對每個imudata append

```python
imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                    for k in set(IMU_DATA_STRUCTURE)}
imudata = {
    "NANO33_W": np.array((1., 2., 3.)),
    "NANO33_A": np.array((-1., -2., -3.)),
    "ADXL_A": np.array((4., 5., 6.)),
    "TIME": (1.5,)
}
print(imudataArray)
for i in range(5):
    imudataArray = dictOperation(imudataArray, imudata, "APPEND")
print(imudataArray)
```

results:

```python
{'NANO33_W': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'ADXL_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'TIME': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)]}
{'NANO33_W': [array([1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6.])], 'NANO33_A': [array([-1., -1., -1., -1., -1.]), array([-2., -2., -2., -2., -2.]), array([-3., -3., -3., -3., -3.])], 'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5])}

```

2. 測試在main裡 對memsImuReader發送來的imudata append
   
```python
data1 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                for k in set(IMU_DATA_STRUCTURE)}
data2 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
            for k in set(IMU_DATA_STRUCTURE)}
imudata = {
    "NANO33_W": np.array((1., 2., 3.)),
    "NANO33_A": np.array((-1., -2., -3.)),
    "ADXL_A": np.array((4., 5., 6.)),
    "TIME": (1.5,)
}

for i in range(5):
    data1 = dictOperation(data1, imudata, "APPEND")

print(data1)
print(data2)
data1["TIME"] = [data1["TIME"]]
for i in range(3):
    data2 = dictOperation(data2, data1, "APPEND")
print(data2)
```

```python
{'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5]), 'NANO33_A': [array([-1., -1., -1., -1., -1.]), array([-2., -2., -2., -2., -2.]), array([-3., -3., -3., -3., -3.])], 'NANO33_W': [array([1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6.])]}
{'TIME': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_W': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'ADXL_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)]}
{'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
       1.5, 1.5]), 'NANO33_A': [array([-1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,
       -1., -1.]), array([-2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2.,
       -2., -2.]), array([-3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3.,
       -3., -3.])], 'NANO33_W': [array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6.])]}

```

## file_manager

此method用來管理要新增與關上的檔案，定義:
```python
def file_manager(isopen=False, name="notitle", fnum=0):

isopen = True: 開啟檔案
isopen = False: 關上已開啟的檔案 or 不做任何事

return bool, fd

bool: 若開啟檔案成功回傳True，否則False
fd: 若開啟檔案成功回傳obj，否則None

```
### 使用

在要打開檔案處與結束處放入 (此處為main裡按下read button 與 stop button處)

```python
def start(self):
    self.act.readIMU()
    self.act.isRun = True
    self.act.start()
    # 跟file_manager要一個空間，並開啟"imu1.txt"檔案，若成功則isFileOpen為True，
    #File_fd為檔案描述符
    self.isFileOpen, self.File_fd= cmn.file_manager(self.top.save_rb.isChecked(), "imu1.txt")


def stop(self):
    self.act.isRun = False
    self.top.save_rb.setChecked(False)
    #當引述isopen為False時，若有先開啟了檔案，則file_manager會根據fnum引數來關閉檔案，
    #此處無fnum代表預設為第0個檔案; 若無先開啟檔案，則什麼事也不做。
    self.isFileOpen, self.File_fd= cmn.file_manager(self.top.save_rb.isChecked(), "imu1.txt")
```

若在執行的py裡只使用到一個存取檔案，則funm不需填入，預設為0。若超過一個則需加上對應編號，注意開與關需成對出現，其中open_status: bool 需由使用者控制輸出，開檔: True, 關檔: False
目前設定同一個py只能開啟兩個檔案，若益擴增需至common.py裡將fd 之 None list擴增

```python
fd = [None, None]
```

```python
def start1:
    self.isFileOpen1, self.File_fd1= cmn.file_manager(open_status1, "imu1.txt", 0)

def start2:
    self.isFileOpen2, self.File_fd2= cmn.file_manager(open_status2, "imu2.txt", 1)

def stop1:
    self.isFileOpen1, self.File_fd1= cmn.file_manager(open_status1, "imu1.txt", 0)

def stop2:
    self.isFileOpen2, self.File_fd2= cmn.file_controller(open_status2, "imu2.txt", 1)

```

## saveData2File

此 mathod搭配file_manager使用，將file_manager 回傳之 isopen 與 fd 丟入，再將欲寫入的 data 與 fomat丟入即可。 注意 data 形式為 list: 
eg. data = [data1, data2, data3........]，其中data(n) 可為array

```python
def saveData2File(isopen: bool = False, data: list = None, fmt: str = " ", file: object = None):
```

### 使用
```python
data = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
            , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]]

data_fmt = "%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f"

cmn.saveData2File(self.__isFileImuOpen, data, data_fmt, self.__FileImu_fd)
```
