# common function usage

此 module 定義常用到的 methods

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
