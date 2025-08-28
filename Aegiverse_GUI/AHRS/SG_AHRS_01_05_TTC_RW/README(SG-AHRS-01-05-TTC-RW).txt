#20250729
#20250505
1.新增460800 baudrate。
2.新增log的顯示功能介面與內部串接的部分。
misalignment
	1.將misalignment的Update功能建置完成。
	2.當修改參數，該參數控制項背景會變黃色，且更新時只會更新有被修改的控制項參數。
	3.更新回填參數後，會將控制項的外觀(背景)改回預設值。
	4.新增load misalignment file的功能。
	5.parameter與misalignment，若dump出現錯誤會跳出錯誤視窗。
	6.修改misalignment的檢查key是否存在的部分。(因為新增了其他輸入參數至控制項的方法，在一塊其他function也有可能使用到，所以做一些	調整。)
parameter
	1.新增load misalignment file功能。
	2. 修改檢查key值是否存在的function。
	3.修改key是否存在，若不存在會跳出視窗說明的function。
	4.新增log於回填參數的function。
	5.將更新功能的回填參數function，可以只更新被修改的參數。


#20250423
#20250428
1.修改misalignment參數顯示的問題。
2.新增回來Roll、Yaw、Pitch的文字顯示功能。
3.修改卡爾曼功能的使用，將原本parameter中設定卡爾曼功能移除，另外在menu新增卡爾曼參數的設定功能，方便之後轉為對外版本使用。
------------------
4.將存儲問題進行修改，使用降版的PySide6達到可以儲存的功能。

#20250324
1.調整Attitude Indicator的介面，logo圖片的大小。
2.設置error log串接執行的流程，調整之前設置錯誤的部分。

#20250307
1.將Attitude Indicator的介面套至此AHRS的版本中，確認可以正常使用，且中心點始終在pitch的刻度上。
2.將parameter功能修改為與相同型號的舊版儀器有相容性，如果parameter有控制項外框是顯示紅框，代表該控制項的key值在回傳數據中撈取不到，然後在將數據回填完到控制項中之後，因有key值找不到的狀況發生會跳出提醒視窗說明。


#20241211
1.使用"SG-AHRS-01-02-RD-RW"的版本修改成此版本。
2.新增選取baudrate的功能。
3.新增選擇啟動與停止指令的功能。
4.修改加速度計X軸選項的勾選判斷問題。


#20240902

1.修改介面使用的文字。


# 20240911

1.將經度轉換成dps的部分移除掉。(現在儀器都是直接DPS輸出)