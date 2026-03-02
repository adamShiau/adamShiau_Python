# 20251225
Copy 自 IRIS_IMU_Ver2.3，修改給HINS用

# 20250915
1. 搭配IRIS1_MCU_V1.5，新增SG_AHRS_01_08_TTC_RW 修改項目

# 20250808
1.修改parameter執行dump的channel部分，將WX與WZ的指令channel對調。
2.修改misalignment執行dump的GX、GZ的參數值要對調。

# 20250729
1.修改儲存溫度的小數點位數，改為顯示到第三位小數點。
2.修改FOG介面勾選X與Z的軸通道，兩個軸數據互換(在read的部分更改)。

# 20250725
1.修正parameter參數設定問題，當遇到負數時會無法正確轉換IEEE754浮點數，因此新增判斷有號數的程式碼，處理IEEE754轉換數值的過程。

#20250609
1.修改misalignment load file的功能，將Gyro與加速度計分開來載入參數(Load File)，所以如果是Load Gyro File，就只會載入到Gyro的控制項中，若是Load Acceleration File則是載入到加速度計的控制項中。
2.修改當要使用Load File功能時，會先判斷是否有執行dump功能，且有dump出參數顯示在介面上。
3.修改匯出功能，需要先判斷是否有執行dump功能，且有dump出參數顯示在介面上，才能執行匯出功能。

# 20250605

1.parameter
	(1)新增匯入與匯出參數的功能。
	(2)將Update功能移除，修改回之前一輸入參數就寫入設備的方法。
2.misalignment
	(1)新增匯入與會出參數的功能。
	(2)將Update功能移除，改為一輸入參數就寫入設備。