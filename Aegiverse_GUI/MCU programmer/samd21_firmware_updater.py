# -*- coding: utf-8 -*-
"""
SAMD21 Firmware Updater (Nano 33 IoT bootloader, bossac-based)
--------------------------------------------------------------
- One-file PySide6 GUI
- Port scan (app port), log window, progress bar
- 1200-bps touch -> detect bootloader port -> bossac flash with --offset=0x2000
- Cross-platform bossac lookup (Windows Arduino15 path included; extend for macOS/Linux)
- Requires: PySide6, pyserial

Usage
-----
python samd21_firmware_updater.py

Notes
-----
- Place your 'firmware.bin' next to this script, or use "Browse..." to choose it.
- You can also put bossac in ./tools/ (bossac.exe on Windows, bossac on macOS/Linux).
- On macOS/Linux, make sure bossac is executable: chmod +x tools/bossac
"""

import os
import sys
import time
import subprocess
from dataclasses import dataclass
from typing import Optional, Set

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, Signal, QObject

import serial
import serial.tools.list_ports
from PySide6.QtGui import QTextCursor


# ----------------------------- Configuration -----------------------------
DEFAULT_FIRMWARE_NAME = "firmware.bin"
# For Arduino SAMD21 (Nano 33 IoT) the application offset is typically 0x2000
FLASH_OFFSET_HEX = "0x2000"

# ----------------------------- Utilities -----------------------------
def list_ports() -> list[str]:
    return [p.device for p in serial.tools.list_ports.comports()]

def ports_set() -> Set[str]:
    return set(list_ports())

def touch_1200bps(port_name: str, timeout_s: float = 0.3) -> None:
    # Open at 1200 bps then close — triggers bootloader
    with serial.Serial(port=port_name, baudrate=1200, timeout=timeout_s):
        time.sleep(0.2)

def wait_new_bootloader_port(previous_ports: Set[str], timeout_s: float = 6.0) -> Optional[str]:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        now = ports_set()
        diff = sorted(now - previous_ports)
        if diff:
            return diff[0]
        time.sleep(0.1)
    return None

def bossac_supports_long_offset(bossac_path: str) -> bool:
    """檢查 bossac 是否支援 --offset= 參數"""
    try:
        cp = subprocess.run([bossac_path, "--help"], capture_output=True, text=True)
        help_txt = (cp.stdout or "") + (cp.stderr or "")
        return "--offset" in help_txt  # 有出現就代表支援
    except Exception:
        return False

def find_bossac() -> Optional[str]:
    """
    Tries in this order:
    1) ./tools/bossac(.exe)
    2) Arduino15 packages path (Windows). Extend as needed for macOS/Linux.
    """
    # Local tools folder
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(here, "tools", "bossac.exe"),
        os.path.join(here, "tools", "bossac"),
    ]

    # Windows Arduino15 path
    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        appdata = os.path.join(userprofile, "AppData", "Local")
        arduino15 = os.path.join(appdata, "Arduino15", "packages", "arduino", "tools", "bossac")
        if os.path.isdir(arduino15):
            for v in sorted(os.listdir(arduino15), reverse=True):
                p_exe = os.path.join(arduino15, v, "bossac.exe")
                p_unx = os.path.join(arduino15, v, "bossac")
                if os.path.exists(p_exe):
                    candidates.append(p_exe)
                if os.path.exists(p_unx):
                    candidates.append(p_unx)

    # macOS Homebrew or Arduino.app bundled paths could be added here if needed

    for c in candidates:
        if os.path.exists(c):
            return c
    return None

# ----------------------------- Worker -----------------------------
@dataclass
class FlashTask:
    app_port: str
    firmware_path: str
    bossac_path: str
    offset_hex: str = FLASH_OFFSET_HEX

class FlashWorker(QObject):
    progress = Signal(int)          # 0..100 (coarse phases)
    log = Signal(str)               # log text
    finished = Signal(bool, str)    # (success, summary)

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
        self.log.emit("步驟 1/4：記錄目前已存在的序列埠...")
        before = ports_set()
        self.progress.emit(10)

        if self._abort: 
            self.finished.emit(False, "已中止")
            return

        self.log.emit("步驟 2/4：以 1200 bps 觸發 bootloader...")
        try:
            touch_1200bps(self.task.app_port)
        except Exception as e:
            self.finished.emit(False, f"1200bps 觸發失敗：{e}")
            return
        self.progress.emit(25)

        if self._abort: 
            self.finished.emit(False, "已中止")
            return

        self.log.emit("等待新的 bootloader 埠出現...")
        boot_port = wait_new_bootloader_port(before, timeout_s=8.0)
        if not boot_port:
            self.finished.emit(False, "找不到 bootloader 埠，請嘗試按兩下 RESET 再試。")
            return
        self.log.emit(f"偵測到 bootloader 埠：{boot_port}")
        self.progress.emit(40)

        if self._abort: 
            self.finished.emit(False, "已中止")
            return

        # Step 3: bossac flash
        self.log.emit("步驟 3/4：執行 bossac 寫入（這段期間進度列會以忙碌模式顯示）...")
        ok, outlog = self._flash_with_bossac(boot_port)
        self.log.emit(outlog)
        self.progress.emit(90)

        if not ok:
            self.finished.emit(False, "bossac 寫入失敗，詳見上方日誌。")
            return

        self.log.emit("步驟 4/4：裝置重啟並回到應用程式...")
        time.sleep(1.2)
        self.progress.emit(100)
        self.finished.emit(True, "更新完成")

    def _flash_with_bossac(self, boot_port: str) -> tuple[bool, str]:
        cmd = [
            self.task.bossac_path,
            "-i", "-d",
            f"--port={boot_port}",
            "-U", "true", "-i",
            "-e", "-w", "-v",
            "-b",  # ← 關鍵：boot from flash，Arduino 版本會自用 0x2000
            self.task.firmware_path,
            "-R"
        ]
        self.log.emit("執行指令：\n  " + " ".join(cmd))

        self.log.emit("執行指令：\n  " + " ".join(cmd))
        try:
            # Use Popen to stream logs
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError:
            return False, "找不到 bossac 執行檔。"
        except Exception as e:
            return False, f"無法啟動 bossac：{e}"

        lines = []
        # Emit a few 'busy' progress bumps so users feel alive
        bump_points = [50, 55, 60, 65, 70, 75, 80, 85]
        idx = 0
        while True:
            line = proc.stdout.readline()
            if line == "" and proc.poll() is not None:
                break
            if line:
                lines.append(line.rstrip("\n"))
                self.log.emit(line.rstrip("\n"))
                # Optional: bump progress a bit
                if idx < len(bump_points):
                    self.progress.emit(bump_points[idx])
                    idx += 1

            if self._abort:
                proc.kill()
                return False, "使用者中止"

        rc = proc.returncode
        full = "\n".join(lines)
        ok = (rc == 0 and ("Verify successful" in full or "Verify successful" in full))
        return ok, full

    def abort(self):
        self._abort = True

# ----------------------------- Main Window -----------------------------
class UpdaterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAMD21 Firmware Updater")
        self.resize(780, 560)

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Row 1: Port select + Refresh
        row1 = QtWidgets.QHBoxLayout()
        self.port_cb = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("重新掃描埠")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        row1.addWidget(QtWidgets.QLabel("應用程式 COM 埠："))
        row1.addWidget(self.port_cb, 1)
        row1.addWidget(self.refresh_btn)
        layout.addLayout(row1)

        # Row 2: Firmware path + Browse
        row2 = QtWidgets.QHBoxLayout()
        self.fw_edit = QtWidgets.QLineEdit()
        self.fw_browse = QtWidgets.QPushButton("選擇韌體檔...")
        self.fw_browse.clicked.connect(self.browse_fw)
        row2.addWidget(QtWidgets.QLabel("韌體檔 (.bin)："))
        row2.addWidget(self.fw_edit, 1)
        row2.addWidget(self.fw_browse)
        layout.addLayout(row2)

        # Row 3: Bossac path + detect
        row3 = QtWidgets.QHBoxLayout()
        self.bossac_edit = QtWidgets.QLineEdit()
        self.bossac_detect = QtWidgets.QPushButton("自動尋找 bossac")
        self.bossac_detect.clicked.connect(self.autofind_bossac)
        row3.addWidget(QtWidgets.QLabel("bossac 路徑："))
        row3.addWidget(self.bossac_edit, 1)
        row3.addWidget(self.bossac_detect)
        layout.addLayout(row3)

        # Row 4: Buttons (Update / Abort)
        row4 = QtWidgets.QHBoxLayout()
        self.update_btn = QtWidgets.QPushButton("開始更新")
        self.update_btn.clicked.connect(self.on_update)
        self.abort_btn = QtWidgets.QPushButton("中止")
        self.abort_btn.setEnabled(False)
        self.abort_btn.clicked.connect(self.on_abort)
        row4.addStretch(1)
        row4.addWidget(self.update_btn)
        row4.addWidget(self.abort_btn)
        layout.addLayout(row4)

        # Progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Log
        self.log_edit = QtWidgets.QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumBlockCount(2000)
        layout.addWidget(self.log_edit, 1)

        # Status bar
        self.status = self.statusBar()

        # Thread/worker placeholders
        self.thread: Optional[QtCore.QThread] = None
        self.worker: Optional[FlashWorker] = None

        # Initial fill
        self.refresh_ports()
        # Pre-fill firmware and bossac if possible
        here = os.path.abspath(os.path.dirname(__file__))
        fw_default = os.path.join(here, DEFAULT_FIRMWARE_NAME)
        if os.path.exists(fw_default):
            self.fw_edit.setText(fw_default)
        bossac = find_bossac()
        if bossac:
            self.bossac_edit.setText(bossac)

    def append_log(self, text: str):
        self.log_edit.appendPlainText(text)
        # Autoscroll to end
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QTextCursor.End)  # ← 這裡用 QTextCursor.End
        self.log_edit.setTextCursor(cursor)
        self.log_edit.ensureCursorVisible()

    def refresh_ports(self):
        self.port_cb.clear()
        ports = list_ports()
        self.port_cb.addItems(ports)
        self.status.showMessage(f"找到 {len(ports)} 個序列埠。")

    def browse_fw(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇韌體檔 (.bin)", "", "Binary (*.bin);;All (*.*)")
        if p:
            self.fw_edit.setText(p)

    def autofind_bossac(self):
        p = find_bossac()
        if p:
            self.bossac_edit.setText(p)
            self.status.showMessage("已找到 bossac。")
        else:
            QtWidgets.QMessageBox.warning(self, "找不到 bossac", "請手動指定 bossac 路徑，或將 bossac 放到 ./tools/ 目錄。")

    def on_update(self):
        app_port = self.port_cb.currentText().strip()
        fw = self.fw_edit.text().strip()
        bossac = self.bossac_edit.text().strip()

        if not app_port:
            QtWidgets.QMessageBox.warning(self, "缺少參數", "請先選擇應用程式的 COM 埠。")
            return
        if not os.path.exists(fw):
            QtWidgets.QMessageBox.warning(self, "缺少韌體", f"找不到韌體檔：\n{fw}")
            return
        if not os.path.exists(bossac):
            QtWidgets.QMessageBox.warning(self, "找不到 bossac", f"bossac 不存在：\n{bossac}")
            return

        # Prepare worker
        self.update_btn.setEnabled(False)
        self.abort_btn.setEnabled(True)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.status.showMessage("開始更新...")
        self.append_log("==== 開始更新 ====")

        self.thread = QtCore.QThread(self)
        task = FlashTask(app_port=app_port, firmware_path=fw, bossac_path=bossac)
        self.worker = FlashWorker(task)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.on_finished)
        self.thread.start()

    def on_abort(self):
        if self.worker:
            self.worker.abort()
            self.append_log("嘗試中止中...")

    @QtCore.Slot(int)
    def on_progress(self, v: int):
        # For bossac stage, we leave it determinate but bump occasionally
        self.progress.setRange(0, 100)
        self.progress.setValue(v)

    @QtCore.Slot(bool, str)
    def on_finished(self, ok: bool, summary: str):
        self.append_log("==== 完成 ====" if ok else "==== 失敗 ====")
        self.append_log(summary)
        self.status.showMessage(summary, 5000)
        self.update_btn.setEnabled(True)
        self.abort_btn.setEnabled(False)
        if self.thread:
            self.thread.quit()
            self.thread.wait(2000)
            self.thread = None
        self.worker = None

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = UpdaterWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
