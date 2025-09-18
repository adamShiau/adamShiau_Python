# -*- coding: utf-8 -*-
"""
SAMD21 Firmware Updater (Auto-detect bossac options)
---------------------------------------------------
- 一個獨立可執行的 PySide6 GUI
- 埠掃描、韌體檔選擇、bossac 路徑、自動進入 bootloader、燒錄與 log 視窗
- 會自動偵測 bossac 支援的參數：
    1) 如果支援 --offset → 用 --offset=0x2000
    2) 如果支援 -o → 用 -o 0x2000
    3) 兩者都沒有 → 用 -b (Arduino 客製版 bossac 內建 0x2000)
"""

import os, sys, time, subprocess
from dataclasses import dataclass
from typing import Optional, Set

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QTextCursor
import serial, serial.tools.list_ports

DEFAULT_FIRMWARE_NAME = "firmware.bin"
FLASH_OFFSET_HEX = "0x2000"

# --------- Utility functions ---------
def list_ports() -> list[str]:
    return [p.device for p in serial.tools.list_ports.comports()]

def ports_set() -> Set[str]:
    return set(list_ports())

def touch_1200bps(port_name: str, timeout_s: float = 0.3):
    with serial.Serial(port=port_name, baudrate=1200, timeout=timeout_s):
        time.sleep(0.2)

def wait_new_bootloader_port(previous_ports: Set[str], timeout_s: float = 8.0) -> Optional[str]:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        now = ports_set()
        diff = sorted(now - previous_ports)
        if diff:
            return diff[0]
        time.sleep(0.1)
    return None

def find_bossac() -> Optional[str]:
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(here, "tools", "bossac.exe"),
        os.path.join(here, "tools", "bossac"),
    ]
    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        appdata = os.path.join(userprofile, "AppData", "Local")
        arduino15 = os.path.join(appdata, "Arduino15", "packages", "arduino", "tools", "bossac")
        if os.path.isdir(arduino15):
            for v in sorted(os.listdir(arduino15), reverse=True):
                p_exe = os.path.join(arduino15, v, "bossac.exe")
                p_unx = os.path.join(arduino15, v, "bossac")
                if os.path.exists(p_exe): candidates.append(p_exe)
                if os.path.exists(p_unx): candidates.append(p_unx)
    for c in candidates:
        if os.path.exists(c): return c
    return None

def bossac_capabilities(bossac_path: str) -> dict:
    caps = {'long_offset': False, 'short_offset': False, 'has_b_flag': False}
    try:
        cp = subprocess.run([bossac_path, "--help"], capture_output=True, text=True)
        txt = (cp.stdout or "") + (cp.stderr or "")
        if "--offset" in txt: caps['long_offset'] = True
        if "\n  -o" in txt or " -o " in txt: caps['short_offset'] = True
        if "\n  -b" in txt or " -b " in txt: caps['has_b_flag'] = True
    except Exception:
        pass
    return caps

# --------- Worker ---------
@dataclass
class FlashTask:
    app_port: str
    firmware_path: str
    bossac_path: str
    offset_hex: str = FLASH_OFFSET_HEX

class FlashWorker(QtCore.QObject):
    progress = QtCore.Signal(int)
    log = QtCore.Signal(str)
    finished = QtCore.Signal(bool, str)

    def __init__(self, task: FlashTask):
        super().__init__()
        self.task = task
        self._abort = False

    @QtCore.Slot()
    def run(self):
        try:
            self._run_impl()
        except Exception as e:
            self.finished.emit(False, f"例外錯誤：{e}")

    def _run_impl(self):
        self.progress.emit(0)
        self.log.emit(f"選擇的應用程式埠：{self.task.app_port}")
        before = ports_set()
        self.progress.emit(10)

        self.log.emit("步驟 2/4：以 1200 bps 觸發 bootloader...")
        try:
            touch_1200bps(self.task.app_port)
        except Exception as e:
            self.finished.emit(False, f"1200bps 觸發失敗：{e}")
            return
        self.progress.emit(25)

        self.log.emit("等待新的 bootloader 埠出現...")
        boot_port = wait_new_bootloader_port(before, 8.0)
        if not boot_port:
            self.finished.emit(False, "找不到 bootloader 埠，請按兩下 RESET 再試。")
            return
        self.log.emit(f"偵測到 bootloader 埠：{boot_port}")
        self.progress.emit(40)

        ok, outlog = self._flash_with_bossac(boot_port)
        self.log.emit(outlog)
        self.progress.emit(90)

        if not ok:
            self.finished.emit(False, "bossac 寫入失敗")
            return
        self.progress.emit(100)
        self.finished.emit(True, "更新完成")

    def _flash_with_bossac(self, boot_port: str) -> tuple[bool, str]:
        caps = bossac_capabilities(self.task.bossac_path)
        if caps['long_offset']:
            offset_args = [f"--offset={self.task.offset_hex}"]
            boot_flag = []
        elif caps['short_offset']:
            offset_args = ["-o", self.task.offset_hex]
            boot_flag = []
        else:
            offset_args = []
            boot_flag = ["-b"]
        cmd = [
            self.task.bossac_path,
            "-i", "-d",
            f"--port={boot_port}",
            "-U", "true", "-i",
            "-e", "-w", "-v",
            *offset_args,
            *boot_flag,
            self.task.firmware_path,
            "-R"
        ]
        self.log.emit(f"偵測結果：{caps} → 指令使用：{' '.join(offset_args + boot_flag) or '(無 offset, -b)'}")
        self.log.emit("執行指令：\n  " + " ".join(cmd))
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            return False, f"無法啟動 bossac：{e}"
        lines = []
        while True:
            line = proc.stdout.readline()
            if line == "" and proc.poll() is not None:
                break
            if line:
                self.log.emit(line.rstrip())
                lines.append(line.rstrip())
        rc = proc.returncode
        full = "\n".join(lines)
        return (rc == 0 and "Verify successful" in full), full

# --------- GUI ---------
class UpdaterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAMD21 Firmware Updater")
        self.resize(800, 580)

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        row1 = QtWidgets.QHBoxLayout()
        self.port_cb = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("重新掃描埠")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        row1.addWidget(QtWidgets.QLabel("應用程式 COM 埠："))
        row1.addWidget(self.port_cb, 1)
        row1.addWidget(self.refresh_btn)
        layout.addLayout(row1)

        row2 = QtWidgets.QHBoxLayout()
        self.fw_edit = QtWidgets.QLineEdit()
        self.fw_browse = QtWidgets.QPushButton("選擇韌體檔...")
        self.fw_browse.clicked.connect(self.browse_fw)
        row2.addWidget(QtWidgets.QLabel("韌體檔 (.bin)："))
        row2.addWidget(self.fw_edit, 1)
        row2.addWidget(self.fw_browse)
        layout.addLayout(row2)

        row3 = QtWidgets.QHBoxLayout()
        self.bossac_edit = QtWidgets.QLineEdit()
        self.bossac_detect = QtWidgets.QPushButton("自動尋找 bossac")
        self.bossac_detect.clicked.connect(self.autofind_bossac)
        row3.addWidget(QtWidgets.QLabel("bossac 路徑："))
        row3.addWidget(self.bossac_edit, 1)
        row3.addWidget(self.bossac_detect)
        layout.addLayout(row3)

        row4 = QtWidgets.QHBoxLayout()
        self.update_btn = QtWidgets.QPushButton("開始更新")
        self.update_btn.clicked.connect(self.on_update)
        self.abort_btn = QtWidgets.QPushButton("中止")
        self.abort_btn.setEnabled(False)
        row4.addStretch(1)
        row4.addWidget(self.update_btn)
        row4.addWidget(self.abort_btn)
        layout.addLayout(row4)

        self.progress = QtWidgets.QProgressBar()
        layout.addWidget(self.progress)

        self.log_edit = QtWidgets.QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        layout.addWidget(self.log_edit, 1)

        self.status = self.statusBar()

        self.thread = None
        self.worker = None
        self.refresh_ports()
        here = os.path.abspath(os.path.dirname(__file__))
        fw_default = os.path.join(here, DEFAULT_FIRMWARE_NAME)
        if os.path.exists(fw_default): self.fw_edit.setText(fw_default)
        bossac = find_bossac()
        if bossac: self.bossac_edit.setText(bossac)

    def append_log(self, text: str):
        self.log_edit.appendPlainText(text)
        self.log_edit.moveCursor(QTextCursor.End)

    def refresh_ports(self):
        self.port_cb.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            desc = f"{p.device} — {p.description}"
            if p.hwid:
                # 顯示 VID/PID 部分，通常在 hwid 內
                desc += f" ({p.hwid.split()[0]})"
            self.port_cb.addItem(desc, userData=p.device)
        self.status.showMessage(f"找到 {len(ports)} 個序列埠")

    def browse_fw(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇韌體檔 (.bin)", "", "Binary (*.bin);;All (*.*)")
        if p: self.fw_edit.setText(p)

    def autofind_bossac(self):
        p = find_bossac()
        if p:
            self.bossac_edit.setText(p)
            self.status.showMessage("已找到 bossac")
        else:
            QtWidgets.QMessageBox.warning(self, "找不到 bossac", "請手動指定 bossac 路徑")

    def on_update(self):
        idx = self.port_cb.currentIndex()
        app_port = self.port_cb.itemData(idx)  # 真正的 COM 埠名稱
        fw = self.fw_edit.text().strip()
        bossac = self.bossac_edit.text().strip()
        if not app_port:
            QtWidgets.QMessageBox.warning(self, "缺少參數", "請先選擇應用程式埠")
            return
        if not os.path.exists(fw):
            QtWidgets.QMessageBox.warning(self, "缺少韌體", f"找不到韌體檔：\n{fw}")
            return
        if not os.path.exists(bossac):
            QtWidgets.QMessageBox.warning(self, "找不到 bossac", f"bossac 不存在：\n{bossac}")
            return
        self.update_btn.setEnabled(False)
        self.append_log("==== 開始更新 ====")

        self.thread = QtCore.QThread(self)
        self.worker = FlashWorker(FlashTask(app_port, fw, bossac))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, ok: bool, summary: str):
        self.append_log("==== 完成 ====" if ok else "==== 失敗 ====")
        self.append_log(summary)
        self.update_btn.setEnabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UpdaterWindow()
    w.show()
    sys.exit(app.exec())
