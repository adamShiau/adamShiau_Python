import folium
import os

# 你可以定義三組經緯度數據（每組10個點）
data_group1 = [(23.56090399, 119.62943268),(23.56090481, 119.62943175),(23.56090532, 119.62943169),(23.56089357 ,119.6294382),
               (23.5608559, 119.62945392),(23.56090814, 119.62943662),(23.56083153 , 119.62948225),(23.56097238, 119.62946043 ),
               (23.56088369, 119.62944276),(23.5608957 , 119.62945676)]
data_group2 = [(23.56092535, 119.62947772),(23.5609122, 119.62944604),(23.56085246, 119.62946229),(23.56091545 ,119.62946313),
               (23.56091789, 119.62946209),(23.56090814, 119.62943662),(23.56090808, 119.62943642),(23.56092908, 119.6294277 ),
               (23.56090724, 119.62943441),(23.56092542, 119.6294776)]
data_group3 = [(23.56096612, 119.62945928),(23.56095247, 119.62944651),(23.56089849, 119.62946918),(23.56094121, 119.62945119),
               (23.56089136, 119.62945505),(23.56082531, 119.629475 ),(23.56083874, 119.62947192),(23.56084676, 119.62946921),
               (23.56088858, 119.62944481),(23.56087684, 119.6294497)]

# 參考經緯度點
reference_point = (23.5608877, 119.629432)

# 定義地圖中心
map_center = reference_point

# 建立 Folium 地圖
m = folium.Map(location=map_center, zoom_start=24)

# 定義顏色和 Marker 樣式
colors = ['blue', 'purple', 'orange']  # 修改組別顏色
markers = ['circle', 'star', 'triangle']

# 繪製三組數據點
# for i, (group, color, marker) in enumerate(zip([data_group1, data_group2, data_group3], colors, markers)):
#     for point in group:
#         folium.Marker(
#             location=point,
#             popup=f'Group {i+1} Point',
#             icon=folium.Icon(color=color, icon='info-sign')  # 修改每組圖標顏色
#         ).add_to(m)

# 繪製三組數據點，使用 CircleMarker 簡化圖示
for i, (group, color) in enumerate(zip([data_group1, data_group2, data_group3], colors)):
    for point in group:
        folium.CircleMarker(
            location=point,
            radius=5,  # 圓點大小
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f'Group {i+1} Point'
        ).add_to(m)

# 加入參考點 Marker，使其顯得顯眼
folium.Marker(
    location=reference_point,
    popup='Reference Point',
    icon=folium.Icon(color='green', icon='info-sign', icon_color='white', prefix='fa')  # 設為綠色
).add_to(m)

# 加入參考點圓形區域（半徑 50 公尺）
folium.Circle(
    location=reference_point,
    radius=15,  # 半徑為 50 公尺
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.01
).add_to(m)

# 保存地圖
m.save('map_with_multiple_groups.html')
print("地圖已成功保存！")
