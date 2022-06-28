""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import logging

import pandas as pd
import numpy as np
from numpy import sin, cos, arctan2
import time

from myLib.myNavigation import planar_Navigation
import matplotlib.pyplot as plt

GOOGLE_EARTH_BLUE_START = ('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n' +
                           '<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n' +
                           '<Document>\n' +
                           '<Name>Session 1</Name>\n' +
                           '<Style id=\"redline\">\n' +
                           '<LineStyle>\n' +
                           '<color>ffff140a</color>\n' +
                           '<width>5</width>\n' +
                           '</LineStyle>\n' +
                           '</Style>\n' +
                           '<Placemark>\n' +
                           '<styleUrl>#redline</styleUrl>\n' +
                           '<LineString>\n' +
                           '<extrude>1</extrude>\n' +
                           '<tessellate>1</tessellate>\n' +
                           '<altitudeMode>clampedToGround</altitudeMode>\n' +
                           '<coordinates>')

GOOGLE_EARTH_BLACK_START = ('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n' +
                            '<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n' +
                            '<Document>\n' +
                            '<Name>Session 1</Name>\n' +
                            '<Style id=\"redline\">\n' +
                            '<LineStyle>\n' +
                            '<color>ff000000</color>\n' +
                            '<width>5</width>\n' +
                            '</LineStyle>\n' +
                            '</Style>\n' +
                            '<Placemark>\n' +
                            '<styleUrl>#redline</styleUrl>\n' +
                            '<LineString>\n' +
                            '<extrude>1</extrude>\n' +
                            '<tessellate>1</tessellate>\n' +
                            '<altitudeMode>clampedToGround</altitudeMode>\n' +
                            '<coordinates>')

GOOGLE_EARTH_END = ('</coordinates>\n' +
                    '</LineString>\n' +
                    '</Placemark>\n' +
                    '</Document>\n' +
                    '</kml>')


def main():
    filename = '0627_rt_2.txt'

    file_vbox = open('VBOX_' + "rt_2" + '.kml', 'w')
    file_vbox.writelines(GOOGLE_EARTH_BLACK_START)
    Var = pd.read_csv(filename, comment='#', skiprows=0, chunksize=None)
    # print(Var)
    print('read done')
    t_start = time.perf_counter()
    t = np.array(Var['time'])  # s
    wz = np.array(Var['fog'])  # dps
    # wz = np.array(Var['wz'])  # dps
    speed = np.array(Var['speed']) / 3.6  # m/s
    hei = np.array(Var['Altitude'])  # m
    head = np.array(Var['Heading_KF'])
    vbox_ori_lon = Var['Longitude']
    vbox_ori_lat = Var['Latitude']
    vbox_lon_valid = Var['Longitude'] > 0
    vbox_lat_valid = Var['Latitude'] > 0
    vbox_lon = Var['Longitude'].loc[vbox_lon_valid]
    vbox_lat = Var['Latitude'].loc[vbox_lat_valid]
    man_idx = abs(vbox_lon - 121.714305).idxmin()
    man_idx2 = abs(vbox_lon - 121.790530).idxmin()
    print('man_idx:　%d, %f' % (man_idx, vbox_lon[man_idx]))
    print('man_idx2:　%d, %f' % (man_idx2, vbox_lon[man_idx2]))
    # man_idx = 10000
    # vbox_ori_lon.plot()
    # vbox_lon.plot()
    size = int(len(t) / 1) - 0
    lat0 = vbox_lat[man_idx]
    lon0 = vbox_lon[man_idx]
    hei0 = hei[man_idx]
    head0 = -head[man_idx] - 2.5 + 1.1
    print('size: ', size)
    print('head0: ', head0)
    # head0 = -284
    track_lon = np.empty(0)
    track_lat = np.empty(0)
    navi = planar_Navigation.planarNav()
    navi.set_init(lat0=lat0, hei0=hei0, head0=head0, lon0=lon0)
    navi.t0 = t[man_idx] - 0.01
    file_imu = open('IMU_' + "rt_2_" + str(head0) + '_man.kml', 'w')
    file_imu.writelines(GOOGLE_EARTH_BLUE_START)
    # '''
    idx = 0
    print('t[%d]: %f' %(man_idx, t[man_idx]))
    print('t[%d]: %f' % (man_idx2, t[man_idx2]))
    dt = (t[man_idx2]-t[man_idx])/3600
    print('dt: ', dt, dt**0.5)
    for i in range(man_idx, man_idx2):
        idx += 1
        ecef_l, ecef_b = navi.track(t=t[i], wz=wz[i], speed=speed[i], hei=hei[i])
        # print('i: ', i)
        # print(ecef_l, ecef_b)
        track_lon = np.append(track_lon, ecef_l)
        track_lat = np.append(track_lat, ecef_b)
        if idx % 10 == 0:
            np.savetxt(file_imu, np.vstack([ecef_l, ecef_b, hei[i]]).T, fmt='%10.7f,%10.7f,%4.2f')
            if vbox_ori_lon[i] != 0 and vbox_ori_lat[i] != 0:
                np.savetxt(file_vbox, np.vstack([vbox_ori_lon[i], vbox_ori_lat[i], hei[i]]).T,
                           fmt='%10.7f,%10.7f,%4.2f')

    t_end = time.perf_counter()
    print('time cost: %f s\n' % (t_end - t_start))
    file_imu.writelines(GOOGLE_EARTH_END)
    file_imu.close()
    file_vbox.writelines(GOOGLE_EARTH_END)
    file_vbox.close()
    plt.plot(track_lon, track_lat, 'b-')
    plt.plot(vbox_lon, vbox_lat, 'r-')
    plt.legend(['IMU', 'VBOX'])
    # '''

    plt.show()


if __name__ == '__main__':
    main()
