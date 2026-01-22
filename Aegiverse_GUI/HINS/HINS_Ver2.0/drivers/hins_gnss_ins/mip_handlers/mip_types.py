class MIP_CONSTANTS:
    # GPIO Feature Enum (0x0C, 0x41)
    FEATURE_MAP = {
        0x00: "UNUSED",
        0x01: "GPIO",
        0x02: "PPS",
        0x03: "ENCODER",
        0x04: "TIMESTAMP",
        0x05: "UART",
    }

    # GPIO Behavior Enum
    BEHAVIOR_MAP = {
        0x00: "UNUSED",
        0x01: "GPIO_INPUT",
        0x02: "GPIO_OUTPUT_LOW",
        0x21: "UART_PORT2_TX",
        0x22: "UART_PORT2_RX",
        0x31: "UART_PORT3_TX",
        0x32: "UART_PORT3_RX",

    }
    # GPIO Pin Mode Enum
    PIN_MODE_MAP = {
        0x00: "OPEN_DRAIN",  # 您提到網頁說 0 是 Open Drain
        0x01: "PULL_DOWN",  # 假設 1 是 Push Pull (範例)
        0x02: "PULL_UP",
    }