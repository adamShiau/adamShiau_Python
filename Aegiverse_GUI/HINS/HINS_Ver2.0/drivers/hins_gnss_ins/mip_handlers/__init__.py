# drivers/hins_gnss_ins/mip_handlers/__init__.py
from .base_set_0x01 import BaseSet0x01
from .threeDM_set_0x0c import ThreeDMSet0x0C
from .system_set_0x7f import SystemSet0x7F

# 實例化各個 Handler
_base_handler = BaseSet0x01()
_threeDM_handler = ThreeDMSet0x0C()
_system_handler = SystemSet0x7F()

# 建立 Descriptor Set 到 Handler 的全域映射表
MIP_SET_REGISTRY = {
    0x01: _base_handler,
    0x0C: _threeDM_handler,
    0x7F: _system_handler,
}