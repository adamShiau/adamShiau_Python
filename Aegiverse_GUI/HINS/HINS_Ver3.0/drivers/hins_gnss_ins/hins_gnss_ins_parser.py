# drivers/hins_gnss_ins/hins_gnss_ins_parser.py
# -*- coding:UTF-8 -*-
from .mip_handlers import MIP_SET_REGISTRY
# from .mip_handlers.base_set_0x01 import BaseSet0x01
# from .mip_handlers.threeDM_set_0x0c import ThreeDMSet0x0C
# from .mip_handlers.system_set_0x7f import SystemSet0x7F


class HinsGnssInsParser:
    def __init__(self):
        self.handlers = MIP_SET_REGISTRY

    def parse(self, packet: list):
        """
        V1 Protocol 解析器 (依據 ack_codec_v1.cpp)
        Header: 6 bytes [FA, Type, Cmd, Status, Len_L, Len_H]
        Payload: 從 Index 6 開始
        """
        if not packet: return None

        mip_payload = []
        idx = 0
        found_mip = False

        # --- 掃描與解包 (Scanner) ---
        while idx < len(packet):

            # 1. 檢查 SOF (0xFA)
            if packet[idx] == 0xFA:
                # 確保 Header 完整 (至少 6 bytes)
                if idx + 6 > len(packet): break

                # 讀取關鍵欄位
                # Index 4, 5 是長度 (Little Endian)
                payload_len = packet[idx + 4] | (packet[idx + 5] << 8)
                v1_type = packet[idx + 1]

                # 計算封包總長 = Header(6) + Payload + Checksum(2)
                total_pkt_len = 6 + payload_len + 2

                # 確保數據流足夠讀取完整封包
                if idx + total_pkt_len > len(packet):
                    break

                    # 2. 判斷是否為 RESULT (0xA2) 且有內容
                if v1_type == 0xA2 and payload_len > 0:
                    # Payload 從 Index 6 開始
                    payload_start = idx + 6
                    candidate = packet[payload_start: payload_start + payload_len]

                    # 檢查 MIP Header (75 65)
                    if len(candidate) >= 2 and candidate[0] == 0x75 and candidate[1] == 0x65:
                        mip_payload = candidate
                        found_mip = True
                        break  # 找到目標，結束掃描

                # 移動到下一個 V1 封包
                idx += total_pkt_len

            # 容錯：如果不是 FA，可能是裸露的 MIP 數據 (75 65)
            elif packet[idx] == 0x75:
                if idx + 1 < len(packet) and packet[idx + 1] == 0x65:
                    mip_payload = packet[idx:]
                    found_mip = True
                    break
                else:
                    idx += 1
            else:
                idx += 1

        if not found_mip or not mip_payload:
            return None

        # --- MIP 解析與分派 (Dispatcher) ---
        if len(mip_payload) < 4: return None

        desc_set_byte = mip_payload[2]
        mip_len = mip_payload[3]

        handler = self.handlers.get(desc_set_byte)
        if not handler:
            return {"desc_set": hex(desc_set_byte), "fields": [], "note": "No Handler"}

        parsed_results = []
        # MIP Field 從 Index 4 開始
        field_region = mip_payload[4: 4 + mip_len]

        f_idx = 0
        while f_idx < len(field_region):
            if f_idx >= len(field_region): break
            f_len = field_region[f_idx]
            if f_len < 2: break

            if f_idx + f_len > len(field_region): break

            f_desc = field_region[f_idx + 1]
            f_body = field_region[f_idx + 2: f_idx + f_len]

            res = handler.parse_field(f_desc, f_body)
            parsed_results.append(res)
            f_idx += f_len

        return {
            "desc_set": hex(desc_set_byte),
            "fields": parsed_results
        }