此程式改寫3_readPIG，新增encoderReader 與 vboxReader 兩個thread。
main 在按下connect 後即啟動這兩個Thread，這兩個thread會用pyqtSignal
傳數據到main裡分別接收處。

## vbox: 

主要工作為按下connect時接收VBOX數據，按下read時依據當下對平面導航設初始參數。

```python
vboxReader:
    self.vboxdata_qt.emit(vboxdata)

    def readIMU(self):
        self.writeImuCmd(2, 1)
        self.navi.set_init(lat0=self.Latitude, lon0=self.Longitude, head0=self.Heading, hei0=self.Altitude)

    @property
    def vboxdata(self):
        return self.__vboxdata

    @vboxdata.setter
    def vboxdata(self, val):
        self.__vboxdata = val

main:
    # connect後啟動vboxReader之thread，每次都會emit data 到 show_vbox
    self.vbox.vboxdata_qt.connect(self.show_vbox)

    # connect 後啟動 encoder 與 vbox thread
    def connect(self):
        self.encoder.connectServer()
        self.vbox.connect(self.__connector_vbox, 'COM11', 115200)
        self.encoder.isRun = True
        self.vbox.isRun = True
        self.encoder.start()
        self.vbox.start()

    # 按下read後使用定義在act之setter對4個初始參數設值，之後執行self.act.readIMU()，
    # 裡面會設定初始參數，只有head值可以另外在gui的le設定。

    def start(self):
        # set planar navi. init value
        self.act.Heading = self.head0
        self.act.Latitude = self.lat0
        self.act.Longitude = self.lon0
        self.act.Altitude = self.hei0
        self.top.headset_le.le_filename.setText(str(self.head0))

        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()


    # 將vboxdata使用定義在act的setter傳過去，取出要顯示的部分data並
    # show在label，之後將經度與緯度傳到collectVboxNaviData()
    # 此處在取出值時用全域變數來接，是為了按下start後對平面導航設初始值。
    def show_vbox(self, vboxdata):
        self.act.vboxdata = vboxdata
        self.head0 = vboxdata['Heading_from_KF']
        self.lat0 = vboxdata['Latitude']
        self.lon0 = vboxdata['Longitude']
        self.hei0 = vboxdata['Altitude']
        sats = vboxdata['GPS_sats']
        self.top.head_lb.lb.setText(str(self.head0))
        self.top.lat_lb.lb.setText(str(self.lat0))
        self.top.lon_lb.lb.setText(str(self.lon0))
        self.top.alt_lb.lb.setText(str(self.hei0))
        self.top.sat_lb.lb.setText(str(int(sats)))
        self.collectVboxNaviData(self.lon0, self.lat0)

    # 控制經度與緯度的輸出rate，由self.navi_rate決定。
    # self.navi_rate接到naviRate_le，可由GUI輸入值。
    # 最後接到plotvboxNavi來出圖
    def collectVboxNaviData(self, lon, lat):
        period = 1 / self.navi_rate
        if (np.abs(time.perf_counter() - self.tcnt1)) > period:
            self.tcnt1 = time.perf_counter()
            self.vbox_lon = np.append(self.vbox_lon, lon)
            self.vbox_lat = np.append(self.vbox_lat, lat)
            lon_array = self.vbox_lon
            lat_array = self.vbox_lat
            size = len(self.vbox_lat)
            if size > 1000:
                lon_array = self.vbox_lon[size - 1000:size + 1]
                lat_array = self.vbox_lat[size - 1000:size + 1]
            if not self.press_stop:
                self.plotvboxNavi(lon_array, lat_array)

    def plotvboxNavi(self, lon, lat):
        if self.top.plot2_showTrack_cb.cb_1.isChecked():
            self.top.plotrt.ax2.clear()
            self.top.plotrt.ax2.setData(lon, lat)
        else:
            self.top.plotrt.ax2.clear()
```