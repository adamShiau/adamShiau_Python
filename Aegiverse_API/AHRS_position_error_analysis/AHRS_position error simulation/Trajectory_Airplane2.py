from math import atan2
import folium
import numpy as np
from pyproj import Transformer


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
file_path_list = [
    # 'C:/Users/user/Downloads/240023-20241120T072154Z-001/240023/point_20241120_151128.txt',
    # 'C:/Users/user/Downloads/240023-20241120T072154Z-001/240023/point_20241120_161805.txt',

    "./pos_ADIS16505-2_20241107_1026.csv",
    "./pos_ADIS16505-2_20241108_1212.csv",
    "./pos_ADIS16505-2_20241112_1133.csv",
    # "./pos_ADIS16505-2_20241113_1131.csv",
    # "./pos_ADIS16505-2_20241118_1936.csv",
    # "./pos_ADIS16505-2_20241119_1907.csv",
    # "./pos_ADIS16505-2_20241120_2048.csv",
    # "./pos_ADIS16505-2_20241121_1919.csv",
    # "./pos_ADIS16505-2_20241122_1312.csv",
    # "./pos_ADIS16505-2_20241122_1312_forAHRS.csv",

    "./pos_EPSON M-G366_20241112_1143.csv",
    "./pos_EPSON M-G366_20241113_1131.csv",
    "./pos_EPSON M-G366_20241115_0957.csv",
    # "./pos_EPSON M-G366_20241119_1907.csv",
    # "./pos_EPSON M-G366_20241120_2048.csv",
    # "./pos_EPSON M-G366_20241121_1920.csv",
    # "./pos_EPSON M-G366_20241122_1312.csv",
    # "./pos_20241030_182830_1_2.csv",
    # "./pos_20241101_201310_1_2.csv",
    # "./pos_20241108_194629_1_2.csv",
]

NUM_AHRS_DATA = 2
Theta_Rotation_In_degree = -1.5

color_list = [["blue"]*NUM_AHRS_DATA,
              ["yellow"]*10,
              ["red"]*10]

theta_list = np.full(NUM_AHRS_DATA, Theta_Rotation_In_degree)
output_file_path = './map_with_path.html'
##################################################################
##################################################################


if __name__ == "__main__":
    # 建立地圖，中心為第一個座標
    color_list = np.hstack([color_list[0], color_list[1], color_list[2]])
    theta_list = np.deg2rad(np.hstack((theta_list, [0]*20)))
    target_pt = [23.5608877, 119.629432]
    start_pt = []
    map_object = folium.Map(location=target_pt, zoom_start=16)
    # 讀取座標數據
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

        print(file_path)
        print(f"誤差角度 (deg)\t：{ang:.1f}")
        print(f"移動距離 (m)  \t：{dis_end:.0f}")
        print(f"誤差距離 (m)  \t：{np.sum(vec_error ** 2) ** 0.5:.0f}")
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
