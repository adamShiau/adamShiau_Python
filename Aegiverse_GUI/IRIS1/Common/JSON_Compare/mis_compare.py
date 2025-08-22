import json

def compare_mis_check(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().strip().splitlines()

    # 分割上下兩部分
    split_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("{"):
            split_index = i
            break

    first_part = lines[:split_index]
    json_part = "".join(lines[split_index:])  # 合併 JSON 部分

    # 解析第一部分
    dict1 = {}
    for line in first_part:
        if "," in line:
            idx_str, val_str = line.split(",")
            idx = idx_str.strip()
            val = int(val_str.strip())
            dict1[idx] = val

    # 解析 JSON 部分
    dict2 = json.loads(json_part)

    # 比較
    all_keys = sorted(set(dict1.keys()) | set(dict2.keys()), key=int)
    for key in all_keys:
        val1 = dict1.get(key, None)
        val2 = dict2.get(key, None)
        if val1 != val2:
            print(f"Mismatch at index {key}: first={val1}, json={val2}")
    print("比較完成")

# 使用方式
compare_mis_check("mis_check.txt")
