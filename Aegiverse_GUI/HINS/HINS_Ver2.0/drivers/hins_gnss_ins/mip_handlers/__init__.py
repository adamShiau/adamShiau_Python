# drivers/hins_gnss_ins/mip_handlers/__init__.py
from .base_set_0x01 import BaseSet0x01
from .system_set_0x0c import SystemSet0x0C
# 未來可加入 from .sensor_set_0x80 import SensorSet0x80

# 實例化各個 Handler
_base_handler = BaseSet0x01()
_system_handler = SystemSet0x0C()

# 建立 Descriptor Set 到 Handler 的全域映射表
MIP_SET_REGISTRY = {
    0x01: _base_handler,
    0x0C: _system_handler,
    # 0x80: _sensor_handler
}