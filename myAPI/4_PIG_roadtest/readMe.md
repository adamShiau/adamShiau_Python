此程式改寫3_readPIG，新增encoderReader 與 vboxReader 兩個thread。
main 在按下connect 後即啟動這兩個Thread，這兩個thread會用pyqtSignal
傳數據到main裡分別接收處。
vbox: 

```python
vboxReader:
    self.vboxdata_qt.emit(vboxdata)

    @property
    def vboxdata(self):
        return self.__vboxdata

    @vboxdata.setter
    def vboxdata(self, val):
        self.__vboxdata = val

main:
    # emit connect to show_vbox
    self.vbox.vboxdata_qt.connect(self.show_vbox)

    # 將vboxdata使用定義在act的setter傳過去，取出要顯示的部分data並
    # show在label，之後將經度與緯度傳到collectVboxNaviData()
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