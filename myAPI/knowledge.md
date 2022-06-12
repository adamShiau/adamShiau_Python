# python 小知識

- [python 小知識](#python-小知識)
  - [package vs module](#package-vs-module)
  - [gui 之自創 widget 傳送觸發條件方法](#gui-之自創-widget-傳送觸發條件方法)
  - [在不同 .py 傳送變數方法](#在不同-py-傳送變數方法)
## package vs module

1. package 是資料夾，裡面存放很多的 .py 檔案
2. .py 檔案稱為module
3. package 跟 module 都可以被import 成為一個物件。 import package時會自動去抓
   資料夾裡的 \_ \_init_ _.py 
4. package 有 \_ \_ path _ _ 此屬性，,module 沒有
   ```python
    # test.py
    import myLib
    print(myLib)
    print(myLib.NAME)
    print(myLib.__path__)
    ```
    ```python
    # myLib/__init__.py
    print('importing myLib pkg')

    __version__ = '1.0'

    NAME = 'NAME_LIB'
    ```
    ``` command
    輸出: 
    importing myLib pkg
    <module 'myLib' from 'C:\\Users\\adam\\Documents\\GitHub\\adamShiau_Python\\myAPI\\myLib\\__init__.py'>
    NAME_LIB
    ['C:\\Users\\adam\\Documents\\GitHub\\adamShiau_Python\\myAPI\\myLib'    
   ```


## gui 之自創 widget 傳送觸發條件方法

一般的做法是先生成該 obj 後再用 connect 方法連到某個函數來觸發，但當此 widget 存在好幾個 obj 而觸發條件只有一個的話，那麼每個 obj 都要 connect 到相同的函數會讓整個頁面變的冗長。 
比如說有七個開關，每個開關代表不同的事件，但同時只有一個開關可以開，我們可以先產生一個 class 來生成七個開關，接著把這七個開關都連到定義在此 class 裡的某個 connect mathod，在連接時使用 lambda 寫法把自己的 obj 傳入:
``` python
self.rb1.toggled.connect(lambda: self.btnstate_connect(self.rb1))
```
接著在 connect method 裡使用 @property_setter 方法來設值，之後就可以直接讀此值來當作trigger 條件了。

```python

# 此範例可以直接讀 class.btn_status來看是哪個按鈕被按了

class radioButtonBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        self.rb1 = QRadioButton(name1)
        self.rb2 = QRadioButton(name2)

        self.rb1.toggled.connect(lambda: self.btnstate_connect(self.rb1))
        self.rb2.toggled.connect(lambda: self.btnstate_connect(self.rb2))

    def btnstate_connect(self, btn):
        if btn.isChecked():
            self.btn_status = btn.text()

    @property
    def btn_status(self):
        return self.__btn_status

    @btn_status.setter
    def btn_status(self, state):
        self.__btn_status = state
```

## 在不同 .py 傳送變數方法
1. 另外生成一個 global_variable.py將變數定義在裡面，其他 module 則將其 import 進來使用。
2. 把變數存放在 package 的 \_ \_init_ _.py 中，所有 module 去該處存取。
3. 在主 module 一開始就import builtins，並生成新的變數屬性，然後所有其他的 module 便可在一開始也 import builtins 使用該屬性，用這招的好處是可以在其他 module剛被 import 進來時就得到一個參數值來做後續的操作。
   
   ```python
    # 主 module.py
    import builtins

    builtins.LOGGER_NAME = 'test'

    # 其他 module
    import builtins

    if hasattr(builtins, 'LOGGER_NAME'):
        logger_name = builtins.LOGGER_NAME
    else:
        logger_name = 'test2_logger_name'
   ```