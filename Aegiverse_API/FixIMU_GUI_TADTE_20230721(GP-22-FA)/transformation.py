import math

import numpy
import numpy as np


# WGS84橢球
class WGS84:
    def __init__(self):
        self.a = 6378137
        self.e = 0.08181919
        self.b = 6356752.3142
        self.e2 = math.sqrt(self.a ** 2 - self.b ** 2) / self.b
        self.f = (self.a - self.b) / self.a
        self.we = 7.292115e-5  # (rad/s)


w_84 = WGS84()


class Quaternion:
    def __init__(self, *args):
        """input type:
        Quaternion
        Rotate matrix (b2l)
        ndarray of pitch, roll, yaw
        pitch, roll, yaw"""
        if isinstance(args[0], Quaternion):
            """Created by Quaternion"""
            self.R_b2l = args[0].R_b2l
            self.q = args[0].q
            self.ori = args[0].ori
        elif isinstance(args[0], np.ndarray) and args[0].shape == (3, 3):
            """Created by R_b2l"""
            self.R_b2l = args[0].copy()
            self.genQbyR()
            self.genORIbyR()
        elif isinstance(args[0], np.ndarray) and args[0].shape == (4,):
            """Created by q"""
            self.q = args[0].copy()
            self.genRbyQ()
            self.genORIbyR()
        else:
            """Created by Euler angle"""
            if isinstance(args[0], np.ndarray) and args[0].shape == (3,):
                pitch, roll, yaw = args[0]
            else:
                pitch, roll, yaw = args
            # self.R_b2l = cord_b2l(pitch, roll, yaw)
            self.genQbyOri(pitch, roll, yaw)
            self.genRbyQ()
            self.ori = np.array([pitch, roll, yaw])
            # self.gen_Q_by_R()
            # self.gen_ori_by_R()
            self.theta = np.sqrt(pitch ** 2 + roll ** 2 + yaw ** 2)
            self.OMG = np.array([[0, yaw, -roll, pitch],
                                 [-yaw, 0, pitch, roll],
                                 [roll, -pitch, 0, yaw],
                                 [-pitch, -roll, -yaw, 0]])

    def rotate(self, ori_pitch, ori_roll, ori_yaw, dt=1 / 100):
        # the angle of rotation respect to b-frame
        [wx, wy, wz] = [ori_pitch, ori_roll, ori_yaw]
        new_omg = np.array([[0, wz, -wy, wx],
                            [-wz, 0, wx, wy],
                            [wy, -wx, 0, wz],
                            [-wx, -wy, -wz, 0]]) * dt
        theta = np.sqrt(wx ** 2 + wy ** 2 + wz ** 2) * dt
        if theta > 0:
            c_ = 2 * (np.cos(theta / 2) - 1)
            s_ = 2 / theta * np.sin(theta / 2)
            upd_term = c_ * np.eye(4) + s_ * new_omg
            self.q = self.q + 0.5 * upd_term @ self.q
            if self.q[3] < -1 or self.q[3] > 1:
                self.q[3] = np.clip(self.q[3], -1, 1)
            self.genRbyQ()
            self.genORIbyR()

    def multiply(self, arg):
        """if the input is a ndarray or Quaternion, return a Quaternion\n
        if the input is two ndarray, return a ndarray"""
        if isinstance(arg, Quaternion):
            new_q = self.FourByFour(self.q, arg.q)
            return Quaternion(new_q)
        elif isinstance(arg, np.ndarray):
            if arg.shape == (3,):
                arg = np.array([*arg, 0])
            vector = self.FourByFour(self.q, arg)
            vector = self.FourByFour(vector, self.T().q)
            return vector

    @staticmethod
    def FourByFour(p, q):
        [p1, p2, p3, p4] = p
        [q1, q2, q3, q4] = q
        new_q = np.array([p4 * q1 + p1 * q4 + p2 * q3 - p3 * q2,
                          p4 * q2 - p1 * q3 + p2 * q4 + p3 * q1,
                          p4 * q3 + p1 * q2 - p2 * q1 + p3 * q4,
                          p4 * q4 - p1 * q1 - p2 * q2 - p3 * q3])
        return new_q

    def T(self):
        """return Quaternion"""
        new_q = self.q
        new_q[1:5] *= -1
        return Quaternion(new_q)

    def genORIbyR(self):
        pitch = np.arctan2(self.R_b2l[2, 1], np.sqrt(self.R_b2l[0, 1] ** 2 + self.R_b2l[1, 1] ** 2))
        yaw = -np.arctan2(self.R_b2l[0, 1], self.R_b2l[1, 1])
        roll = -np.arctan2(self.R_b2l[2, 0], self.R_b2l[2, 2])
        self.ori = np.array([pitch, roll, yaw])

    def genQbyOri(self, pitch, roll, yaw):
        q4 = np.cos(pitch / 2) * np.cos(roll / 2) * np.cos(yaw / 2) + np.sin(pitch / 2) * np.sin(roll / 2) * np.sin(
            yaw / 2)
        q1 = np.sin(pitch / 2) * np.cos(roll / 2) * np.cos(yaw / 2) - np.cos(pitch / 2) * np.sin(roll / 2) * np.sin(
            yaw / 2)
        q2 = np.cos(pitch / 2) * np.sin(roll / 2) * np.cos(yaw / 2) + np.sin(pitch / 2) * np.cos(roll / 2) * np.sin(
            yaw / 2)
        q3 = np.cos(pitch / 2) * np.cos(roll / 2) * np.sin(yaw / 2) - np.sin(pitch / 2) * np.sin(roll / 2) * np.cos(
            yaw / 2)
        self.q = np.array([q1, q2, q3, q4])

    def genQbyR(self):
        """R is a b-frame to l-frame rotation matrix"""
        q4 = 0.5 * np.sqrt(1 + self.R_b2l[0, 0] + self.R_b2l[1, 1] + self.R_b2l[2, 2])
        if q4 < -1 or q4 > 1:
            q4 = np.clip(q4, -1, 1)
        q1 = 1 / 4 * (self.R_b2l[2, 1] - self.R_b2l[1, 2]) / q4
        q2 = 1 / 4 * (self.R_b2l[0, 2] - self.R_b2l[2, 0]) / q4
        q3 = 1 / 4 * (self.R_b2l[1, 0] - self.R_b2l[0, 1]) / q4
        self.q = np.array([q1, q2, q3, q4])

    def genRbyQ(self, q=None):
        if q is None:
            q1, q2, q3, q4 = self.q
            self.R_b2l = np.array(
                [[q1 ** 2 - q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q1 * q2 - q3 * q4), 2 * (q1 * q3 + q2 * q4)],
                 [2 * (q1 * q2 + q3 * q4), -q1 ** 2 + q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q2 * q3 - q1 * q4)],
                 [2 * (q1 * q3 - q2 * q4), 2 * (q2 * q3 + q1 * q4), -q1 ** 2 - q2 ** 2 + q3 ** 2 + q4 ** 2]])
        else:
            q1, q2, q3, q4 = q
            R = np.array(
                [[q1 ** 2 - q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q1 * q2 - q3 * q4), 2 * (q1 * q3 + q2 * q4)],
                 [2 * (q1 * q2 + q3 * q4), -q1 ** 2 + q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q2 * q3 - q1 * q4)],
                 [2 * (q1 * q3 - q2 * q4), 2 * (q2 * q3 + q1 * q4), -q1 ** 2 - q2 ** 2 + q3 ** 2 + q4 ** 2]])
            return R


def Vel_gnss2Vel_en(gnss_vel, heading):
    if len(gnss_vel.shape) == 1:
        azimuth = -heading
        vel_ref = np.array([gnss_vel[0] * np.sin(azimuth),
                            gnss_vel[0] * np.cos(azimuth),
                            gnss_vel[1]])
    else:
        n = gnss_vel.shape[0]
        vel_ref = np.empty((n, 3))
        for i in range(n):
            azimuth = -heading[i]
            vel_ref[i] = np.array([gnss_vel[i, 0] * np.sin(azimuth),
                                   gnss_vel[i, 0] * np.cos(azimuth),
                                   gnss_vel[i, 1]])
    return vel_ref


def vector2skew(raw_vector):
    if isinstance(raw_vector, list):
        vector = np.array(raw_vector)
    elif isinstance(raw_vector, np.ndarray):
        vector = raw_vector.reshape(-1)
    else:
        vector = np.array(raw_vector)
    (x, y, z) = vector
    sk_ma = np.array([[0, -z, y],
                      [z, 0, -x],
                      [-y, x, 0]])
    return sk_ma


def skew2vector(sk_ma):
    x = sk_ma[2, 1]
    y = sk_ma[0, 2]
    z = sk_ma[1, 0]
    vector = np.array([x, y, z])
    return vector


def trans_matrix(x, y, z, scale='big'):
    if scale == 'big':
        # 建立三軸旋轉矩陣，r、p、y由l-frame順時針轉向b-frame
        # 因此b-frame to l-frame需要轉置
        # pitch
        ro_x = np.array([
            [1, 0, 0],
            [0, math.cos(x), math.sin(x)],
            [0, -math.sin(x), math.cos(x)]])
        # roll
        ro_y = np.array([
            [math.cos(y), 0, -math.sin(y)],
            [0, 1, 0],
            [math.sin(y), 0, math.cos(y)]])
        # yaw
        ro_z = np.array([
            [math.cos(z), math.sin(z), 0],
            [-math.sin(z), math.cos(z), 0],
            [0, 0, 1]])

        # 依序以roll, pitch, yaw順序旋轉
        ro = ro_z @ ro_x @ ro_y
        return ro
    elif scale == 'small':
        ro = np.eye(3) - vector2skew([x, y, z])
        return ro
    else:
        print('scale input wrong')


def cord_l2e(latitude, longitude):
    deg_90 = math.radians(90)
    ro_la = trans_matrix(- (deg_90 - latitude), 0, 0)
    ro_lo = trans_matrix(0, 0, -(deg_90 + longitude))
    ro = ro_lo @ ro_la
    return ro


def cord_i2e():
    # we為WGS84參考橢球自轉速度
    ro = trans_matrix(0, 0, w_84.we)
    return ro


def cord_b2l(p, r, y):
    # x軸為pitch, y軸為roll, z軸為yaw
    ro = trans_matrix(-p, -r, -y)
    # roll:以y軸逆時針旋轉→l-frame to b-frame
    # b-frame to l-frame = 順時針轉回去
    return ro


def cord_b2e(p, r, y, latitude, longitude):
    ro_b2l = cord_b2l(p, r, y)
    ro_l2e = cord_l2e(latitude, longitude)
    ro = ro_l2e @ ro_b2l
    return ro


def cord_b2i(p, r, y, latitude, longitude):
    ro_b2l = cord_b2l(p, r, y)
    ro_l2e = cord_l2e(latitude, longitude)
    ro_e2i = np.transpose(cord_i2e())
    ro = ro_e2i @ ro_l2e @ ro_b2l
    return ro


def llh2xyz(lat, lon, h):
    # 經緯度&xyz皆為地心地固坐標系統
    rn = w_84.a / np.sqrt(1 - (w_84.e * np.sin(lat)) ** 2)
    # 計算x, y, z
    x = (rn + h) * np.cos(lat) * np.cos(lon)
    y = (rn + h) * np.cos(lat) * np.sin(lon)
    z = (rn * (1 - w_84.e ** 2) + h) * np.sin(lat)
    xyz = np.append(x, y)
    xyz = np.append(xyz, z)
    return xyz


def xyz2llh(x, y, z, cal_type='loop'):
    """type can be 'loop' or 'closed'"""
    p = np.sqrt(x ** 2 + y ** 2)
    if cal_type == 'loop':
        my_hei0 = 0
        my_lat0 = np.arctan(z / p / (1 - w_84.e ** 2))
        my_lon = np.arctan2(y, x)
        my_lat, my_hei = 0, 0
        d_la, d_h = 1, 1
        while np.max(d_h) > 1e-4 or np.max(d_la) > 1e-9:  # 1cm精度/6371km =  1.57e-9 (rad)
            r_n = w_84.a / np.sqrt(1 - w_84.e ** 2 * np.sin(my_lat0) ** 2)
            my_hei = np.sqrt(x ** 2 + y ** 2) / np.cos(my_lat0) - r_n
            my_lat = np.arctan(z * (r_n + my_hei) / (np.sqrt(x ** 2 + y ** 2) * (r_n * (1 - w_84.e ** 2) + my_hei)))
            d_la = abs(my_lat - my_lat0)
            d_h = abs(my_hei - my_hei0)
            my_lat0 = my_lat
            my_hei0 = my_hei
    else:
        theta = np.arctan(z * w_84.a / w_84.b / p)
        # 計算經緯度、高程
        my_lon = 2 * np.arctan(y / (x + np.sqrt(x ** 2 + y ** 2)))
        my_lat = np.arctan((z + w_84.e2 ** 2 * w_84.b * np.sin(theta) ** 3) /
                           (p - w_84.e ** 2 * w_84.a * np.cos(theta) ** 3))
        n = w_84.a ** 2 / np.sqrt((w_84.a * np.cos(my_lat)) ** 2 + (w_84.b * np.sin(my_lat)) ** 2)
        my_hei = p / np.cos(my_lat) - n

    llh = np.vstack((my_lat, my_lon))
    llh = np.vstack((llh, my_hei))
    return llh


def dcm_transform(ori_ro, ori_w, fs=100):
    theta = np.sqrt(np.dot(ori_w, ori_w))
    dt = 1 / fs
    omg_w_lb_b = vector2skew(ori_w) * dt
    s = np.sin(theta) / theta
    c = (1 - np.cos(theta)) / theta ** 2
    new_ro = ori_ro @ (np.eye(3) + s * omg_w_lb_b + c * omg_w_lb_b @ omg_w_lb_b)
    return new_ro


def dcm2qut(ro):
    q4 = 0.5 * np.sqrt(1 + ro[0, 0] + ro[1, 1] + ro[2, 2])
    q1 = 1 / 4 * (ro[2, 1] - ro[1, 2]) / q4
    q2 = 1 / 4 * (ro[0, 2] - ro[2, 0]) / q4
    q3 = 1 / 4 * (ro[1, 0] - ro[0, 1]) / q4
    q = np.array([q1, q2, q3, q4])
    return q


def qut_update(ori_q, ori_w, fs=100):
    dt = 1 / fs
    theta = np.sqrt(np.dot(ori_w, ori_w)) * dt
    [wx, wy, wz] = ori_w
    new_omg = np.array([[0, wz, -wy, wx],
                        [-wz, 0, wx, wy],
                        [wy, -wx, 0, wz],
                        [-wx, -wy, -wz, 0]]) * dt
    c_ = 2 * (np.cos(theta / 2) - 1)
    s_ = 2 / theta * np.sin(theta / 2)
    upd_term = c_ * np.eye(4) + s_ * new_omg

    new_q = ori_q + 0.5 * upd_term @ ori_q
    return new_q


def qut2dcm(q):
    q1, q2, q3, q4 = q
    ro_matrix = np.array(
        [[q1 ** 2 - q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q1 * q2 - q3 * q4), 2 * (q1 * q3 + q2 * q4)],
         [2 * (q1 * q2 + q3 * q4), -q1 ** 2 + q2 ** 2 - q3 ** 2 + q4 ** 2, 2 * (q2 * q3 - q1 * q4)],
         [2 * (q1 * q3 - q2 * q4), 2 * (q2 * q3 + q1 * q4), -q1 ** 2 - q2 ** 2 + q3 ** 2 + q4 ** 2]])
    return ro_matrix


def dcm2attitude(ro):
    """:param ro : b2l matrix"""
    pitch = np.arcsin(ro[2, 1])
    yaw = -np.arctan2(ro[0, 1], ro[1, 1])
    roll = -np.arctan2(ro[2, 0], ro[2, 2])
    return [pitch, roll, yaw]


def meridian_radius(lat):
    rm = w_84.a * (1 - w_84.e ** 2) / (1 - w_84.e ** 2 * np.sin(lat) ** 2) ** (3 / 2)
    return rm


def normal_radius(lat):
    rn = w_84.a / np.sqrt(1 - w_84.e ** 2 * np.sin(lat) ** 2)
    return rn


def gravity(pos):
    lat = pos[0]
    height = pos[2]
    a1 = 9.7803267714
    a2 = 0.0052790414
    a3 = 0.0000232718
    a4 = -0.0000030876910891
    a5 = 0.0000000043977311
    a6 = 0.0000000000007211

    gv = a1 * (1 + a2 * np.sin(lat) ** 2 + a3 * np.sin(lat) ** 4) \
         + (a4 + a5 * np.sin(lat) ** 2) * height + a6 * height ** 2
    return gv


def pos_rad2deg(pos_rad):
    new_pos = np.rad2deg(pos_rad[:, :2])
    return np.hstack((new_pos, pos_rad[:, 2].reshape(-1, 1)))


def llh2ENU(pos_llh: np.ndarray):
    ENU = np.empty(pos_llh.shape)
    if pos_llh.shape == (3,):
        pos = pos_llh
        rm_h = meridian_radius(pos[0]) + pos[2]
        rn_h = (normal_radius(pos[0]) + pos[2]) * np.cos(pos[0])
        ENU[:] = [pos[1] * rn_h, pos[0] * rm_h, pos[2]]
    else:
        for i in range(pos_llh.shape[0]):
            pos = pos_llh[i]
            rm_h = meridian_radius(pos[0]) + pos[2]
            rn_h = (normal_radius(pos[0]) + pos[2]) * np.cos(pos[0])
            ENU[i] = [pos[1] * rn_h, pos[0] * rm_h, pos[2]]
    return ENU
