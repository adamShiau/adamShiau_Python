# Aegiverse Planar Dead Reckoning library

__此Library由互宇向量提供給十方資源使用來分析處理從IMU得出之數據，目的為將由起始點開始之相對位置轉換為絕對位置之經緯度，屬機密文件，同雙方簽署之保密協議負保密義務。__


- [Aegiverse Planar Dead Reckoning library](#aegiverse-planar-dead-reckoning-library)
  - [使用方法](#使用方法)
    - [1. 建立類別物件:](#1-建立類別物件)
    - [2. 設定初始值:](#2-設定初始值)
    - [3. 計算經緯度:](#3-計算經緯度)
  - [測試程式 (test.py)](#測試程式-testpy)


## 使用方法

### 1. 建立類別物件:

建立類別`planarNav`的物件, 此物件不帶參數:
```python
myNavi = planarNav()
```

### 2. 設定初始值:

使用類別方法 `set_init(lat0, lon0, hei0, head0)` 設定起始位置初始值:

```python
myNavi.set_init(lat0, lon0, hei0, head0)

lat0: 起始點之緯度, 單位:度, 格式使用十進位表示 ex: 25.005744
lon0: 起始點之經度, 單位:度, 格式使用十進位表示 ex: 120.430231
hei0: 起始點之高度, 單位:米
head0: 起始點與正北之夾角, 單位:度

return: none
```

### 3. 計算經緯度:

使用類別方法 `track(t, wz, speed, hei)` 來得出經緯度:

```python
myNavi.track(t, wz, speed, hei)

t: 時間, 單位:秒
wz: 角速度, 單位:degree/sec
speed: 前行速度, 單位:m/s
hei: 高度, 單位:m

return: 緯度、經度 
```

使用在後製處理數據場合，可將此method放在迴圈裡，再將轉換後的數據儲存至檔案。

## 測試程式 (test.py)

代入起始緯度:24.997959, 經度:121.422696, 高度:100m 
假設朝向正北以速度每秒10米直線飛行100秒(head0=0, speed=10, wz=0)，
理論飛行距離為1km，
驗證程式執行結果:
```python
from planar_Navigation import planarNav

t = 0
myNavi = planarNav();
myNavi.set_init(lat0=24.997959, lon0=121.422696, hei0=100, head0=0)

for i in range(100):
	lat, lon = myNavi.track(t=t, wz=0.0, speed=10, hei=100)
	print(lat, end=', ')
	print(lon)
	t += 1

```

results:
經度無改變，緯度慢慢增加
起點緯度: 24.99795894
終點緯度: 25.006896
假設地球半徑 6400km，
飛行距離: (25.006896 - 24.997959)*pi/180*6400km = 0.99827918366 km

```cmd
PS C:\Users\adam\Desktop\planar_dead_reckoning> python .\test.py
set Navi. init.lat0:  24.997959
set Navi. init.lon0:  121.422696
set Navi. init.hei0:  100
set Navi. init.head0:  0
[121.422696], [24.99795894]
[121.422696], [24.99804921]
[121.422696], [24.99813948]
[121.422696], [24.99822976]
[121.422696], [24.99832003]
[121.422696], [24.9984103]
[121.422696], [24.99850058]
[121.422696], [24.99859085]
[121.422696], [24.99868112]
[121.422696], [24.9987714]
[121.422696], [24.99886167]
[121.422696], [24.99895194]
[121.422696], [24.99904222]
[121.422696], [24.99913249]
[121.422696], [24.99922276]
[121.422696], [24.99931304]
[121.422696], [24.99940331]
.
.
.
[121.422696], [25.00608354]
[121.422696], [25.00617381]
[121.422696], [25.00626408]
[121.422696], [25.00635436]
[121.422696], [25.00644463]
[121.422696], [25.0065349]
[121.422696], [25.00662518]
[121.422696], [25.00671545]
[121.422696], [25.00680572]
[121.422696], [25.006896]
```