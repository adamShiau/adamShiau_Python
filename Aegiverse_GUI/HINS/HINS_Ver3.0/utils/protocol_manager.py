# utils/protocol_manager.py
# -*- coding:UTF-8 -*-
import logging

class ProtocolParser:
    """ 所有協議解析器的基類 (Abstract Class) """
    def __init__(self):
        self.buffer = []
        self.logger = logging.getLogger(f"main.utils.{self.__class__.__name__}")

    def push_byte(self, byte: int):
        """ 逐位元組輸入，完成封包後回傳 list，否則 None """
        raise NotImplementedError

class ProtocolDispatcher:
    """ 派發器：負責將 Serial 數據分發給註冊的 Parser """
    def __init__(self):
        self.parsers = []

    def add_parser(self, parser: ProtocolParser, callback):
        """
        parser: ProtocolParser 子類實例
        callback: 解析成功後呼叫的函數 (通常在 Reader 內)
        """
        self.parsers.append({'p': parser, 'c': callback})

    def feed_data(self, raw_bytes: list):
        """ 接收來自 Connector 的數據流 """
        for byte in raw_bytes:
            for item in self.parsers:
                packet = item['p'].push_byte(byte)
                if packet:
                    item['c'](packet)
                    break # 該 Byte 已被消耗