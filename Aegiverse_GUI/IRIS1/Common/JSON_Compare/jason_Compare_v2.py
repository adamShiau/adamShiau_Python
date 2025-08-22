import json
import re

def extract_json_objects(file_path):
    """從檔案擷取所有 JSON { ... } 物件"""
    results = []
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 找所有 {...} 區塊 (允許跨行)
    matches = re.findall(r"\{.*?\}", text, re.DOTALL)

    for i, m in enumerate(matches, start=1):
        try:
            results.append(json.loads(m))
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON #{i} 解析失敗: {e}")
    return results

def compare_params(file1, file2, show_identical=True):
    params1 = extract_json_objects(file1)
    params2 = extract_json_objects(file2)

    print(f"[INFO] {file1} 擷取到 {len(params1)} 筆 JSON")
    print(f"[INFO] {file2} 擷取到 {len(params2)} 筆 JSON")

    max_len = max(len(params1), len(params2))
    for i in range(max_len):
        if i >= len(params1):
            print(f"Line {i+1}: only in {file2}")
            continue
        if i >= len(params2):
            print(f"Line {i+1}: only in {file1}")
            continue

        dict1, dict2 = params1[i], params2[i]
        diffs = []
        for key in set(dict1.keys()).union(dict2.keys()):
            v1, v2 = dict1.get(key), dict2.get(key)
            if v1 != v2:
                diffs.append((key, v1, v2))

        if diffs:
            print(f"Line {i+1} differences:")
            for key, v1, v2 in sorted(diffs, key=lambda x: int(x[0]) if str(x[0]).isdigit() else str(x[0])):
                print(f"  key {key}: {file1}={v1}, {file2}={v2}")
        elif show_identical:
            print(f"Line {i+1}: identical ✅")

if __name__ == "__main__":
    compare_params("para0.txt", "para2.txt")
