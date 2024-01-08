import numpy as np


class Quaternion:
    def __init__(self, *args):
        """input type:
        Quaternion
        Rotate matrix (b2l)
        ndarray of pitch, roll, yaw
        pitch, roll, yaw"""
        if isinstance(args[0], Quaternion):
            self.R_b2l = args[0].R_b2l
            self.q = args[0].q
            self.orientation = args[0].orientation
        elif isinstance(args[0], np.ndarray) and args[0].shape == (3, 3):
            self.R_b2l = args[0].copy()
            self.gen_Q_by_R()
            self.gen_ori_by_R()
        elif isinstance(args[0], np.ndarray) and args[0].shape == (4,):
            self.q = args[0].copy()
            self.gen_R_by_Q()
            self.gen_ori_by_R()
        else:
            if isinstance(args[0], np.ndarray) and args[0].shape == (3,):
                my_pitch, my_roll, my_yaw = args[0]
            else:
                my_pitch, my_roll, my_yaw = args
            self.R_b2l = cord_b2l(my_pitch, my_roll, my_yaw)
            self.gen_Q_by_R()
            self.gen_ori_by_R()
            self.theta = np.sqrt(my_pitch ** 2 + my_roll ** 2 + my_yaw ** 2)
            self.OMG = np.array([[0, my_yaw, -my_roll, my_pitch],
                                 [-my_yaw, 0, my_pitch, my_roll],
                                 [my_roll, -my_pitch, 0, my_yaw],
                                 [-my_pitch, -my_roll, -my_yaw, 0]])

    def rotate(self, ori_pitch, ori_roll, ori_yaw, dt=1 / 100):
        """OpenGL to IMU\n
        X to -Y\n
        Y to Z\n
        Z to -X
        """
        # the angle of rotation respect to b-frame
        # [wx, wy, wz] = [ori_pitch, ori_roll, ori_yaw]
        [wx, wy, wz] = np.deg2rad([-ori_roll, ori_yaw, -ori_pitch])
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
            self.gen_R_by_Q()
            self.gen_ori_by_R()

    def getRotationArray(self):
        q1, q2, q3, q4 = self.q
        if q4 > 1 or q4 < -1:
            q4 = np.clip(q4, -1, 1)
        theta = np.rad2deg(2 * np.arccos(q4))
        if theta > 360:
            theta -= 360
        elif theta < 0:
            theta += 360
        return [theta, q1, q2, q3]

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

    def gen_Q_by_R(self):
        """R is a b-frame to l-frame rotation matrix"""
        q4 = 0.5 * np.sqrt(1 + self.R_b2l[0, 0] + self.R_b2l[1, 1] + self.R_b2l[2, 2])
        q1 = 1 / 4 * (self.R_b2l[2, 1] - self.R_b2l[1, 2]) / q4
        q2 = 1 / 4 * (self.R_b2l[0, 2] - self.R_b2l[2, 0]) / q4
        q3 = 1 / 4 * (self.R_b2l[1, 0] - self.R_b2l[0, 1]) / q4
        self.q = np.array([q1, q2, q3, q4])

    def gen_ori_by_R(self):
        """R is a b-frame to l-frame rotation matrix"""
        pitch = np.arctan2(self.R_b2l[2, 1], np.sqrt(self.R_b2l[0, 1] ** 2 + self.R_b2l[1, 1] ** 2))
        yaw = -np.arctan2(self.R_b2l[0, 1], self.R_b2l[1, 1])
        roll = -np.arctan2(self.R_b2l[2, 0], self.R_b2l[2, 2])
        self.orientation = np.array([pitch, roll, yaw])

    def gen_R_by_Q(self, q=None):
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

def cord_b2l(p, r, y):
    # x軸為pitch, y軸為roll, z軸為yaw
    ro = trans_matrix(-p, -r, -y)
    # roll:以y軸逆時針旋轉→l-frame to b-frame
    # b-frame to l-frame = 順時針轉回去
    return ro

def trans_matrix(x, y, z, scale='big'):
    if scale == 'big':
        # 建立三軸旋轉矩陣，r、p、y由l-frame順時針轉向b-frame
        # 因此b-frame to l-frame需要轉置
        # pitch
        ro_x = np.array([
            [1, 0, 0],
            [0, np.cos(x), np.sin(x)],
            [0, -np.sin(x), np.cos(x)]])
        # roll
        ro_y = np.array([
            [np.cos(y), 0, -np.sin(y)],
            [0, 1, 0],
            [np.sin(y), 0, np.cos(y)]])
        # yaw
        ro_z = np.array([
            [np.cos(z), np.sin(z), 0],
            [-np.sin(z), np.cos(z), 0],
            [0, 0, 1]])

        # 依序以roll, pitch, yaw順序旋轉
        ro = ro_z @ ro_x @ ro_y
        return ro
    elif scale == 'small':
        ro = np.eye(3) - vector2skew([x, y, z])
        return ro
    else:
        print('scale input wrong')
