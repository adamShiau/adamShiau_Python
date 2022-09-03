# Aegiverse IMU_ROS

本專案為使用PC USB透過serial port與IMU主機做溝通，將IMU數據封包接收完後以ros sensor_msgs/Imu 格式publish出去。


linux 版本: ubuntu 18.04

ros 版本: melodic

python 版本: 2.7

Author: Adam Shiau

Email: adam@aegiverse.com


- [Aegiverse IMU_ROS](#aegiverse-imu_ros)
  - [IMU 規格](#imu-規格)
  - [ROS /Imu msg 輸入參數](#ros-imu-msg-輸入參數)
  - [Running the program](#running-the-program)
    - [step1](#step1)
    - [step2](#step2)
    - [step3](#step3)
    - [step4](#step4)

-----------

## IMU 規格

|     | dynamic range|random walk| Noise Density|  type      |
|:---:|:------------:|:----------:|:------------:|:-----:|
|gyro.x| 250 &deg;/s |0.59 &deg;/$\sqrt{hr}$|35.4 &deg;/hr/$\sqrt{Hz}$|MEMS
|gyro.y| 250 &deg;/s | 0.59 &deg;/$\sqrt{hr}$|35.4 &deg;/hr/$\sqrt{Hz}$|MEMS
|gyro.z| 350 &deg;/s |0.01 &deg;/$\sqrt{hr}$|0.6 &deg;/hr/$\sqrt{Hz}$|FOG|
|accelerometer.x|$\pm 8g$|5.3 mm/s/$\sqrt{hr}$|25 $\mu g/\sqrt{Hz}$|MEMS|
|accelerometer.y|$\pm 8g$|5.3 mm/s/$\sqrt{hr}$|25 $\mu g/\sqrt{Hz}$|MESM|
|accelerometer.z|$\pm 8g$|7.7 mm/s/$\sqrt{hr}$|25 $\mu g/\sqrt{Hz}$|MEMS|

---

## ROS /Imu msg 輸入參數

以下參數值可在 **./rosParameters.py** 設定

* 預設只有角速度與加速度之斜對角部分(Variance)有填值

| python var | unit | description |
|:-----|:-----:|:-----|
|ORI_X、ORI_Y、ORI_Z、ORI_W||Quaternion orientation|
|COV_ORI_XX、COV_ORI_XY、COV_ORI_XZ <br>COV_ORI_YX、COV_ORI_YY、COV_ORI_YZ <br>COV_ORI_ZX、COV_ORI_ZY、COV_ORI_ZZ||Orientation covariance|
|COV_W_XX、 COV_W_XY、COV_W_XZ <br>COV_W_YX、COV_W_YY、COV_W_YZ <br>COV_W_ZX、COV_W_ZY、COV_W_ZZ|$[rad/s]^2$|Angular velocity covariance|
|COV_A_XX、 COV_A_XY、COV_A_XZ <br>COV_A_YX、COV_A_YY、COV_A_YZ <br>COV_A_ZX、COV_A_ZY、COV_A_ZZ|$[m/s^2]^2$|Linear acceleration covariance|

---

## Running the program

IMU上電後，在 terminal 執行下列 command:

### step1

設定USB port name使用權限(假設port name = /dev/ttyUSB0):

```cmd
$ sudo chmod +777 /dev/ttyUSB0
```

### step2

```cmd
$ roscore
```

### step3

```cmd
$ python pigImu_Ros.py ttyUSB0 1 1 
```

|參數名稱|型態|說明|
|:---:|:---:|:---|
|arg[0] |string| 程式名稱|
|arg[1]|string|USB對應的 port name|
|arg[2]|int|[1/0] : [扣除/不扣除] gyro offset|
|arg[3]|int|[1/0] : [扣除/不扣除] accelerometer offset|


### step4

結束執行程式:

```cmd
$ ctrl + c
```


