import json

def load_params(file_path):
    """讀取 txt，每行是一個 JSON，回傳 list of dict"""
    results = []
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[WARN] 第 {i} 行不是合法 JSON，跳過: {e}")
    return results


def compare_params(file1, file2):
    params1 = load_params(file1)
    params2 = load_params(file2)

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
            v1 = dict1.get(key)
            v2 = dict2.get(key)
            if v1 != v2:
                diffs.append((key, v1, v2))

        if diffs:
            print(f"Line {i+1} differences:")
            for key, v1, v2 in diffs:
                print(f"  key {key}: {file1}={v1}, {file2}={v2}")
        else:
            print(f"Line {i+1}: identical")

if __name__ == "__main__":
    compare_params("para0.txt", "para1.txt")
