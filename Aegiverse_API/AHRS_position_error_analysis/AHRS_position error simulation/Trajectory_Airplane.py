from math import atan2
import folium
import numpy as np
from pyproj import Transformer
import os


def wgs84_to_twd97(lat, lon, hei=None, is_3d=False):
    # 定義轉換器
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3826", always_xy=not is_3d)
    # 進行轉換
    if is_3d:
        return np.array(transformer.transform(lon, lat, hei))
    else:
        return np.array(transformer.transform(lon, lat))


##################################################################
##################################################################
file_path1 = r'H:\共用雲端硬碟\Aegiverse_RD\FOG開發\AHRS data\Position_Error_Analysis\SG-1A-EC 240008'
file_path2 = r'H:\共用雲端硬碟\Aegiverse_RD\FOG開發\AHRS data\Position_Error_Analysis\SG-3A-EC 240003'
file_path3 = r'H:\共用雲端硬碟\Aegiverse_RD\FOG開發\AHRS data\Position_Error_Analysis\SG-3A-EC 240004'

file_name11 = 'point_20241126_152846_translated'
file_name12 = 'point_20241126_164953_translated'
file_name13 = 'point_20241126_175156_translated'
file_name14 = 'point_20241127_090512_translated'
file_name15 = 'point_20241127_123741_translated'
file_name17 = 'point_20241128_154500_translated'
file_name19 = 'point_20241129_105220_translated'
file_name111 = 'point_20241127_133836_translated'
file_name112 = 'point_20241127_151621_translated'
file_name113 = 'point_20241127_171015_translated'

file_name21 = 'point_20241128_165127_translated'
file_name22 = 'point_20241128_154457_translated'
file_name23 = 'point_20241126_141347_translated'
file_name24 = 'point_20241128_122139_translated'
file_name25 = 'point_20241128_111316_translated'
file_name26 = 'point_20241127_113325_translated'
file_name27 = 'point_20241127_123748_translated'
file_name28 = 'point_20241127_133841_translated'
file_name29 = 'point_20241126_191027_translated'
file_name20 = 'point_20241128_090310_translated'

file_name31 = 'point_20241128_165131_translated'
file_name32 = 'point_20241128_154458_translated'
file_name33 = 'point_20241127_171011_translated'
file_name34 = 'point_20241128_090309_translated'
file_name35 = 'point_20241127_151614_translated'
file_name36 = 'point_20241126_152848_translated'
file_name37 = 'point_20241126_164949_translated'
file_name38 = 'point_20241126_175153_translated'
file_name39 = 'point_20241127_113318_translated'
file_name30 = 'point_20241127_123744_translated'

# file_name21 = 'point_20241127_133841_translated'
#
# file_name31 = 'point_20241127_151614_translated'

file_path_list = [
    # os.path.join(file_path1, file_name11 + '.txt'),
    # os.path.join(file_path1, file_name12 + '.txt'),
    # os.path.join(file_path1, file_name13 + '.txt'),
    # os.path.join(file_path1, file_name14 + '.txt'),
    # os.path.join(file_path1, file_name15 + '.txt'),
    # os.path.join(file_path1, file_name17 + '.txt'),
    # os.path.join(file_path1, file_name19 + '.txt'),
    # os.path.join(file_path1, file_name111 + '.txt'),
    # os.path.join(file_path1, file_name112 + '.txt'),
    # os.path.join(file_path1, file_name113 + '.txt'),
    #
    # os.path.join(file_path2, file_name21 + '.txt'),
    # os.path.join(file_path2, file_name22 + '.txt'),
    # os.path.join(file_path2, file_name23 + '.txt'),
    # os.path.join(file_path2, file_name24 + '.txt'),
    # os.path.join(file_path2, file_name25 + '.txt'),
    # os.path.join(file_path2, file_name26 + '.txt'),
    # os.path.join(file_path2, file_name27 + '.txt'),
    # os.path.join(file_path2, file_name28 + '.txt'),
    # os.path.join(file_path2, file_name29 + '.txt'),
    # os.path.join(file_path2, file_name20 + '.txt'),
    #
    # os.path.join(file_path3, file_name31 + '.txt'),
    # os.path.join(file_path3, file_name32 + '.txt'),
    # os.path.join(file_path3, file_name33 + '.txt'),
    # os.path.join(file_path3, file_name34 + '.txt'),
    # os.path.join(file_path3, file_name35 + '.txt'),
    # os.path.join(file_path3, file_name36 + '.txt'),
    # os.path.join(file_path3, file_name37 + '.txt'),
    # os.path.join(file_path3, file_name38 + '.txt'),
    # os.path.join(file_path3, file_name39 + '.txt'),
    # os.path.join(file_path3, file_name30 + '.txt'),

    "./pos_ADIS16505-2_20241107_1026.txt",
    "./pos_ADIS16505-2_20241108_1212.txt",
    "./pos_ADIS16505-2_20241112_1133.txt",
    "./pos_ADIS16505-2_20241113_1131.txt",
    "./pos_ADIS16505-2_20241118_1936.txt",
    "./pos_ADIS16505-2_20241119_1907.txt",
    "./pos_ADIS16505-2_20241120_2048.txt",
    "./pos_ADIS16505-2_20241121_1919.txt",
    "./pos_ADIS16505-2_20241122_1312.txt",
    "./pos_ADIS16505-2_20241122_1312_forAHRS.txt",
    # #
    #
    "./pos_EPSON M-G366_20241112_1143.txt",
    "./pos_EPSON M-G366_20241113_1131.txt",
    "./pos_EPSON M-G366_20241115_0957.txt",
    "./pos_EPSON M-G366_20241119_1907.txt",
    "./pos_EPSON M-G366_20241120_2048.txt",
    "./pos_EPSON M-G366_20241121_1920.txt",
    "./pos_EPSON M-G366_20241122_1312.txt",
    "./pos_20241030_182830_1_2.txt",
    "./pos_20241101_201310_1_2.txt",
    "./pos_20241108_194629_1_2.txt",
]

NUM_AHRS_DATA = 0
# Theta_Rotation_In_degree = -114.001
Theta_Rotation_In_degree = -112.892
# Theta_Rotation_In_degree = -113.88

color_list = [
    # ["blue"] * NUM_AHRS_DATA,
    # ["blue"] * 10,
    # ["violet"] * 10,
    # ["brown"] * 10,
    ["yellow"] * 10,
    ["red"] * 10
]

theta_list = np.full(NUM_AHRS_DATA, Theta_Rotation_In_degree)
output_file_path = './map_with_path2.html'



if __name__ == "__main__":
    # 建立地圖，中心為第一個座標
    # color_list = np.hstack([color_list[0], color_list[1], color_list[2], color_list[3], color_list[4]])
    color_list = np.hstack([color_list[0], color_list[1]])
    theta_list = np.deg2rad(np.hstack((theta_list, [0] * 20)))
    target_pt = [23.5608877, 119.629432]
    start_pt = []
    map_object = folium.Map(location=target_pt, zoom_start=16)
    # 讀取座標數據
    diff = np.empty(0)
    cnt = 0
    for color, file_path, theta in zip(color_list, file_path_list, theta_list):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        coordinates = []
        for line in lines:
            line = line.strip()
            if line.startswith("#") or ',' not in line:
                continue
            try:
                lat, lon = map(float, line.split(','))
                coordinates.append((lat, lon))
            except ValueError:
                continue

        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

        c0 = coordinates[0]
        coordinates = (R @ (np.array(coordinates) - c0).T).T + c0


        start_pt = coordinates[0]
        end_pt = coordinates[-1]

        start_pt_enu = wgs84_to_twd97(*start_pt)
        target_pt_enu = wgs84_to_twd97(*target_pt)
        end_pt_enu = wgs84_to_twd97(*end_pt)

        vec_tg = target_pt_enu - start_pt_enu
        vec_end = end_pt_enu - start_pt_enu

        dis_tg = np.sum(vec_tg ** 2) ** 0.5
        dis_end = np.sum(vec_end ** 2) ** 0.5
        ratio = dis_tg / dis_end
        num_data = int(ratio * len(coordinates))
        coordinates = coordinates[:num_data]

        start_pt = coordinates[0]
        end_pt = coordinates[-1]

        start_pt_enu = wgs84_to_twd97(*start_pt)
        target_pt_enu = wgs84_to_twd97(*target_pt)
        end_pt_enu = wgs84_to_twd97(*end_pt)

        vec_tg = target_pt_enu - start_pt_enu
        vec_end = end_pt_enu - start_pt_enu
        dis_tg = np.sum(vec_tg ** 2) ** 0.5
        dis_end = np.sum(vec_end ** 2) ** 0.5

        vec_error = end_pt_enu - target_pt_enu

        ang = np.rad2deg(atan2(*vec_tg) - atan2(*vec_end))
        err_distance = np.sum(vec_error ** 2) ** 0.5
        cnt = cnt + 1
        diff = np.append(diff, err_distance)
        diff_total = np.sum(diff)
        diff_avg = np.mean(diff)
        diff_std = np.std(diff)
        # print(cnt, diff_total, diff_avg, diff_std)
        # print(diff)
        print(file_path)
        print(num_data)
        print('color:', color)
        print('start_pt: ', start_pt)
        print('end_pt: ', end_pt)
        print(f"誤差角度 (deg)\t：{ang:.3f}")
        print(f"移動距離 (m)  \t：{dis_end:.0f}")
        print(f"誤差距離 (m)  \t：{err_distance:.0f}")
        print()

        folium.PolyLine(coordinates, color=color, weight=2.5, opacity=1).add_to(map_object)

    # 在終點設置圓形區域
    folium.PolyLine([start_pt, target_pt], color="green", weight=2.5, opacity=1).add_to(map_object)
    # folium.Circle(
    #     location=target_pt,
    #     radius=400,  # 半徑 400 米
    #     color='red',
    #     fill=True,
    #     fill_opacity=0.3
    # ).add_to(map_object)

    # 保存地圖

    map_object.save(output_file_path)
