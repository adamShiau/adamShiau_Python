class MIP_CONSTANTS:
    # GPIO Feature Enum (0x0C, 0x41)
    FEATURE_MAP = {
        0x00: "UNUSED",
        0x01: "GPIO",
        0x02: "PPS",
        0x03: "ENCODER",
        0x04: "TIMESTAMP",
        0x05: "UART",
        0x06: "EVENT",
    }

    # GPIO Behavior Enum
    BEHAVIOR_MAP = {
        0x00: "NONE",
        0x01: "INPUT",
        0x02: "OUTPUT",
        0x11: "UART1_TX",
        0x12: "UART1_RX",
        0x21: "UART2_TX",
        0x22: "UART2_RX",
        0x10: "PPS_OUTPUT",
        0x20: "PPS_INPUT",
    }