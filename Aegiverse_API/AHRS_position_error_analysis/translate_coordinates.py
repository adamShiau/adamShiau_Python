import numpy as np
import os


def translate_coordinates(file_path, target_lat, target_lon, output_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 提取經緯度數據，忽略 'point' 和日期行
    coordinates = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line == "point":  # 檢查是否為空行或無效行
            continue
        try:
            lat, lon = map(float, line.split(","))
            coordinates.append((lat, lon))
        except ValueError:
            print(f"無法解析的行：{line}")  # 可選：記錄無法解析的行

    if not coordinates:
        print("未找到有效的經緯度數據。")
        return

    # 計算中心點 (以原始數據的平均值作為中心點)
    original_center_lat = coordinates[0][0]
    original_center_lon = coordinates[0][1]


    # 計算平移的偏移量
    lat_offset = target_lat - original_center_lat
    print('lat:', target_lat, original_center_lat, lat_offset)

    lon_offset = target_lon - original_center_lon
    print('lat:', target_lon, original_center_lon, lon_offset)

    # 對所有經緯度應用平移
    translated_coords = [(lat + lat_offset, lon + lon_offset) for lat, lon in coordinates]

    # 將結果保存到新的文件
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for lat, lon in translated_coords:
            out_file.write(f"{lat},{lon}\n")

    print(f"平移完成！結果已保存到 {output_file}")


# 使用該函數
file_path1 = r'H:\共用雲端硬碟\Aegiverse_RD\FOG開發\AHRS data\Position_Error_Analysis\SG-3A-EC 240004'

file_name = 'point_20241127_171011'
file_ext = '.txt'
# file_name = 'pos_20241108_194629_1_2'
# file_ext = '.csv'
full_file_path = os.path.join(file_path1, file_name+file_ext)
full_file_path_out = os.path.join(file_path1, file_name+'_translated.txt')
# full_file_path_out = os.path.join(file_path1, file_name+'.txt')

translate_coordinates(full_file_path, 23.8008019, 120.197621, full_file_path_out)
