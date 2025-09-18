# -*- coding: utf-8 -*-

import os, sys, time, subprocess
from dataclasses import dataclass
from typing import Optional, Set

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QTextCursor
import serial, serial.tools.list_ports

DEFAULT_FIRMWARE_NAME = "firmware.bin"
FLASH_OFFSET_HEX = "0x2000"

import platform
import re
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
    """
    搜尋順序（找到就回傳）：
      1) 使用者自訂環境變數 BOSSAC_PATH
      2) 可執行檔旁的 tools/bossac(.exe)   ← 打包後建議放這
      3) 可執行檔同層的 bossac(.exe)
      4) PyInstaller onefile 的臨時目錄（sys._MEIPASS）下的 tools/
      5) 原始腳本資料夾（__file__）下的 tools/
      6) 目前工作目錄（cwd）下的 tools/
      7) Arduino15 的 bossac（作為 fallback）
    """
    import sys, os
    from pathlib import Path

    def exists(p: Path) -> Optional[str]:
        return str(p) if p and p.exists() else None

    # 1) 環境變數
    env = os.environ.get("BOSSAC_PATH")
    if env and Path(env).exists():
        return env

    # 判斷「可執行檔所在資料夾」與「腳本資料夾」
    if getattr(sys, "frozen", False):
        # PyInstaller 狀態
        exe_dir = Path(sys.executable).parent
        meipass = Path(getattr(sys, "_MEIPASS", exe_dir))
        script_dir = None
    else:
        exe_dir = Path(sys.executable).parent  # 例如 python.exe 所在
        meipass = None
        script_dir = Path(__file__).resolve().parent

    cwd = Path(os.getcwd())

    candidates: list[Path] = []

    # 2) 可執行檔旁的 tools/
    candidates += [
        exe_dir / "tools" / "bossac.exe",
        exe_dir / "tools" / "bossac",
    ]
    # 3) 可執行檔同層
    candidates += [
        exe_dir / "bossac.exe",
        exe_dir / "bossac",
    ]
    # 4) PyInstaller 展開目錄（onefile）
    if meipass:
        candidates += [
            meipass / "tools" / "bossac.exe",
            meipass / "tools" / "bossac",
            meipass / "bossac.exe",
            meipass / "bossac",
        ]
    # 5) 原腳本資料夾
    if script_dir:
        candidates += [
            script_dir / "tools" / "bossac.exe",
            script_dir / "tools" / "bossac",
        ]
    # 6) 工作目錄
    candidates += [
        cwd / "tools" / "bossac.exe",
        cwd / "tools" / "bossac",
    ]

    # 7) Arduino15 fallback（Windows；可自行擴充 macOS/Linux）
    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        appdata = Path(userprofile) / "AppData" / "Local"
        arduino15 = appdata / "Arduino15" / "packages" / "arduino" / "tools" / "bossac"
        if arduino15.exists():
            # 取版本號最大的資料夾為優先
            for v in sorted(arduino15.iterdir(), reverse=True):
                if v.is_dir():
                    candidates += [v / "bossac.exe", v / "bossac"]

    # 回傳第一個存在的
    for c in candidates:
        p = exists(c)
        if p:
            return p

    return None


def normalize_port_for_bossac(port_name: str) -> str:
    """
    在 Windows 上，COM >= 10 建議用 \\\\.\\COMxx 交給底層。
    其他平台或 COM < 10 原樣回傳。
    """
    if platform.system().lower().startswith("win"):
        m = re.match(r"^COM(\d+)$", port_name, re.IGNORECASE)
        if m and int(m.group(1)) >= 10:
            return r"\\.\{}".format(port_name)
    return port_name

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


def get_port_info_map():
    """回傳 {device: ListPortInfo} 的快照，方便之後比對 description/VID/PID。"""
    m = {}
    for p in serial.tools.list_ports.comports():
        m[p.device] = p
    return m

def is_likely_bootloader(port_info) -> bool:
    """用描述或 VID/PID 粗略判斷是否是 bootloader 埠。"""
    if port_info is None:
        return False
    desc = (port_info.description or "").lower()
    # 很多 Arduino/SAMD bootloader 描述會包含 "bootloader" 或 "sam-ba"
    if "bootloader" in desc or "sam-ba" in desc:
        return True
    # 也可用已知的 VID/PID 來判斷；這裡做保守處理，只用描述關鍵字
    return False


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

        # 步驟 1/4
        self.log.emit("步驟 1/4：記錄目前已存在的序列埠...")
        before_map = get_port_info_map()
        before = set(before_map.keys())
        self.progress.emit(10)

        # 若一開始就已在 bootloader，直接用這個埠寫入
        sel_info = before_map.get(self.task.app_port)
        if is_likely_bootloader(sel_info):
            self.log.emit(f"偵測到所選埠 {self.task.app_port} 已是 bootloader，跳過 1200bps 觸發。")
            boot_port = self.task.app_port
        else:
            # 步驟 2/4
            self.log.emit("步驟 2/4：以 1200 bps 觸發 bootloader...")
            try:
                touch_1200bps(self.task.app_port)
            except Exception as e:
                self.finished.emit(False, f"1200bps 觸發失敗：{e}")
                return
            self.progress.emit(25)

            # 等待新埠
            self.log.emit("等待新的 bootloader 埠出現...")
            boot_port = wait_new_bootloader_port(before, timeout_s=8.0)

            # 容錯 A：沒新埠，但原埠仍在且看起來是 bootloader → 用原埠
            if not boot_port:
                after_map = get_port_info_map()
                if self.task.app_port in after_map and is_likely_bootloader(after_map[self.task.app_port]):
                    boot_port = self.task.app_port
                    self.log.emit("未偵測到新埠，但所選埠仍在且像 bootloader，改用原埠寫入。")

            # 容錯 B：沒新埠、原埠也不像；但系統只多出一個埠 → 直接用那個
            if not boot_port:
                now = set(get_port_info_map().keys())
                diff = list(now - before)
                if len(diff) == 1:
                    boot_port = diff[0]
                    self.log.emit(f"未看到明確 bootloader 訊號，但出現單一新埠，改用：{boot_port}")

        if not boot_port:
            self.finished.emit(False, "找不到 bootloader 埠，請按兩下 RESET 再試。")
            return

        self.log.emit(f"偵測到 bootloader 埠：{boot_port}")
        self.progress.emit(40)

        # 等裝置就緒（Windows enumerate 需要一點時間）
        self.log.emit("等待裝置就緒（enumeration）...")
        t0 = time.time()
        while time.time() - t0 < 2.0:  # 最多等 2 秒
            now_ports = set(p.device for p in serial.tools.list_ports.comports())
            if boot_port in now_ports:
                # 再給一點緩衝
                time.sleep(0.4)
                break
            time.sleep(0.1)

        # 步驟 3/4：燒錄
        self.log.emit("步驟 3/4：執行 bossac 寫入（寫入中輸出會即時顯示）...")
        ok, outlog = self._flash_with_bossac(boot_port)
        self.log.emit(outlog)
        self.progress.emit(90)

        if not ok:
            self.finished.emit(False, "bossac 寫入失敗，詳見上方日誌。")
            return

        # 步驟 4/4：收尾
        self.log.emit("步驟 4/4：裝置重啟並回到應用程式...")
        time.sleep(1.2)
        self.progress.emit(100)
        self.finished.emit(True, "更新完成")

    def _flash_with_bossac(self, boot_port: str) -> tuple[bool, str]:
        caps = bossac_capabilities(self.task.bossac_path)

        # 選參數（和你現有邏輯相同）
        if caps['long_offset']:
            offset_args = [f"--offset={self.task.offset_hex}"]
            boot_flag = []
        elif caps['short_offset']:
            offset_args = ["-o", self.task.offset_hex]
            boot_flag = []
        else:
            offset_args = []
            boot_flag = ["-b"]

        # Windows COM>=10 用完整裝置路徑
        bossac_port = normalize_port_for_bossac(boot_port)

        base_cmd = [
            self.task.bossac_path,
            "-i", "-d",
            f"--port={bossac_port}",
            "-U", "true", "-i",
            "-e", "-w", "-v",
            *offset_args,
            *boot_flag,
            self.task.firmware_path,
            "-R"
        ]
        self.log.emit(f"偵測結果：{caps} → 指令使用：{' '.join(offset_args + boot_flag) or '-b（隱含 0x2000）'}")
        self.log.emit(f"bossac 連線埠：{bossac_port}")
        self.log.emit("執行指令（可能自動重試）...")

        # 重試 3 次（0.6s → 1.0s → 1.5s）
        backoffs = [0.6, 1.0, 1.5]
        all_logs = []
        for attempt, delay in enumerate(backoffs, 1):
            cmd = list(base_cmd)
            self.log.emit("  Try #{:d}:\n    {}".format(attempt, " ".join(cmd)))

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
                    line = line.rstrip()
                    lines.append(line)
                    self.log.emit(line)

            rc = proc.returncode
            full = "\n".join(lines)
            all_logs.append(full)

            # 成功條件
            if rc == 0 and ("Verify successful" in full or "Verify successful" in full):
                return True, full

            # 若訊息包含「No device found」或裝置瞬斷，就等一下再重試
            if "No device found" in full or "No serial port found" in full or rc != 0:
                self.log.emit(f"寫入未成功（rc={rc}），{delay}s 後重試...")
                time.sleep(delay)
                # 每次重試前再確認埠還在
                now_ports = set(p.device for p in serial.tools.list_ports.comports())
                if boot_port not in now_ports:
                    self.log.emit("bootloader 埠暫時消失，等待重新出現...")
                    t0 = time.time()
                    while time.time() - t0 < 3.0:
                        now_ports = set(p.device for p in serial.tools.list_ports.comports())
                        if boot_port in now_ports:
                            time.sleep(0.3)
                            break
                        time.sleep(0.1)
                continue

        # 三次都沒成功
        return False, "\n\n--- 專家訊息（彙整） ---\n" + ("\n\n".join(all_logs))


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
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            vidpid = ""
            try:
                if p.vid is not None and p.pid is not None:
                    vidpid = f" (VID:PID={p.vid:04X}:{p.pid:04X})"
            except Exception:
                pass
            label = f"{p.device} — {p.description}{vidpid}"
            self.port_cb.addItem(label, userData=p.device)  # 真正的 COM 名放 userData
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
        app_port = self.port_cb.itemData(idx)  # ← 這裡拿真正的 COM 名稱
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
