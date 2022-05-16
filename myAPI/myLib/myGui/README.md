# myGui 基本使用方法

## Tutorial
https://build-system.fman.io/pyqt5-tutorial

https://www.pythonguis.com/tutorials/plotting-matplotlib/
## 固定使用方式

```python
from PyQt5.QtWidgets import QApplication

'''
code here
'''

if __name__ == "__main__"
app = QApplication([])
app.exec_()
```


## Class QtWidgets
幾乎所有QtGUI使用到的類別都來自此類別
```commandline
from PyQt5.QtWidgets import QApplication, QWidget, QLabel...
```

## Class QWidget 
QWidget 為所以QtGUI類別之容器，一般會先宣告一個名為window的
物件，之後其他的GUI類別會以window.setLayout()形式加到
window裡面。

直接使用:

```python
window = QWidget()
window.show()
```

或是由自己定義類別繼承:
```python
class myWidget(QWidget)
    
obj = myWidget(
obj.show()
)
```

## class mplGraph_1 & mplGraph_2
使用 matplotlib, 使用時先建立類別物件

```python
fig2 = mplGraph_2()
```

### 靜態繪圖
```python
if __name__ == '__main__':
    app = QApplication([])
    fig2 = mplGraph_2()
    fig2.ax1.plot([1, 2, 3])
    fig2.ax2.plot([1, 2, 5])
    fig2.show()
    app.exec_()
```

### 動態繪圖

```python
    def plotdata(self, wz):
        self.top.plot.ax.clear()
        self.wzz = np.append(self.wzz, wz)
        if len(self.wzz) > 1000:
            self.wzz = self.wzz[50:-1]
        print(len(self.wzz))
        print(self.act.readInputBuffer())
        self.top.plot.ax.plot(self.wzz)
        self.top.plot.fig.canvas.draw()
```


## pytgraph

https://www.pythonguis.com/tutorials/plotting-pyqtgraph/


