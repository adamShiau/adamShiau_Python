import numpy as np


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


class AR:
    def __init__(self, std_imu=None):
        self.me = AR_ME()
        self.Predictor = ARPrediction()
        self.Updator = AccLevelingUpdate()
        self.STD = np.array([0.001, 0.001, 0.001, 0.007, 0.007, 0.007])
        self.me.setInit()
        self.setInit(std_imu)

    def setInit(self, std_imu):
        if std_imu is not None:
            self.STD = std_imu
        self.Predictor.setInit(self.STD)
        self.Updator.set_init(self.STD)

    def predict(self, time):
        if self.Predictor.pre_time is not None:
            self.Predictor.input(time, self.me.qut)
            self.Predictor.predict()
        else:
            self.Predictor.pre_time = time

    def ME(self, omg):
        self.me.update(self.Predictor.pre_time, omg)

    def update(self, time, omg, acc):
        self.predict(time)
        self.ME(omg)

        self.Updator.work = False
        if np.abs(np.sum(acc ** 2) ** 0.5 - 9.8) < 0.2:
            abs_pr = np.abs(self.me.qut.ori[:2])
            if abs_pr[0] < np.deg2rad(90) and abs_pr[1] < np.deg2rad(90):
                self.Updator.work = True
                self.Updator.input(time=self.Predictor.pre_time, qut=self.me.qut, acc=acc)
                self.Updator.update(self.Predictor)
                self.Updator.compensate(self.me)
            elif abs_pr[0] < np.deg2rad(90) and False:
                pr = np.array(AccLeveling(*acc))
                alpha = 0.8
                new_pr = alpha * self.me.qut.ori[:2] + (1 - alpha) * pr
                self.me.qut = Quaternion(*new_pr, self.me.qut.ori[2])

    def getRotationArray(self):
        q1, q2, q3, q4 = self.me.qut.q
        if q4 > 1 or q4 < -1:
            q4 = np.clip(q4, -1, 1)
        theta = np.rad2deg(2 * np.arccos(q4))
        if theta > 360:
            theta -= 360
        elif theta < 0:
            theta += 360
        return [theta, q1, q2, q3]


class MechanizationEquation:
    def __init__(self):
        self.pre_time = 0
        # self.pos = np.zeros(3)
        # self.vel = np.zeros(3)
        self.qut = Quaternion(0, 0, 0)
        # self.pre_acc = np.zeros(3)
        # self.pre_acc[2] = 9.8
        self.pre_omg = np.zeros(3)

    def setInit(self, time=None, pre_omg=None):
        if time is not None:
            self.pre_time = time
        if pre_omg is not None:
            self.pre_omg = pre_omg


class AR_ME(MechanizationEquation):
    def __init__(self):
        super().__init__()

    def update(self, time, omg):
        dt = time - self.pre_time
        self.qut.rotate(*omg, dt)
        self.pre_time = time
        self.pre_omg = omg.copy()


class Prediction:
    def __init__(self, dim=9):
        self.F = None
        self.Q = None
        self.P = None
        self.dx = np.zeros((dim, 1))
        self.Q_list = []
        self.P_list = []
        self.r_list = []
        self.alpha = 1.0005

    def predict(self):
        # Because dx is set to zero after compensating, so we can simplify the equation
        # alpha is used to solve the Kalman filter incest problem
        # self.dx = self.F @ self.dx
        self.P = self.alpha ** 2 * self.F @ self.P @ self.F.T + self.Q
        self.P_list.append(np.diag(self.P))
        self.Q_list.append(np.diag(self.Q))

    def renew(self, P: np.ndarray, dx=None):
        if dx is None:
            self.dx = np.zeros((P.shape[0], 1))
        else:
            self.dx = dx.copy()
        self.P = P.copy()

    def get(self, *args):
        output = []
        data = None
        n = len(args)
        for s in args:
            data = getattr(self, f'{s}')
            if isinstance(data, list):
                if isinstance(data[0], np.ndarray):
                    data = np.array(data)
            output.append(data.copy())
        if n == 1:
            return output[0]
        else:
            return output


class ARPrediction(Prediction):
    def __init__(self):
        super().__init__()
        self.var_imu = None
        self.P = np.eye(3)
        self.pre_time = None
        self.gen_F()

    def input(self, time, qut: Quaternion):
        if self.pre_time is not None:
            dt = time - self.pre_time
            self.gen_Q(qut, dt)

        self.pre_time = time

    def setInit(self, std_imu):
        self.var_imu = np.diag([*std_imu]) ** 2

    def gen_F(self):
        """state transition matrix"""
        self.F = np.eye(3)

    def gen_Q(self, qut: Quaternion, dt=0.01):
        """可能需要再調整"""
        ro_mat = qut.R_b2l
        G = ro_mat
        self.Q = self.F @ G @ self.var_imu[0:3, 0:3] @ G.T @ self.F.T * dt


class Update:
    def __init__(self):
        self.HK = None
        self.rm = None
        self.rn = None
        self.H = None
        self.Z = None
        self.dx = None
        self.P = None
        self.R = None
        self.KH = None
        self.Z_list = []
        self.P_list = []
        self.R_list = []
        self.HK_list = []
        self.time_list = []
        self.dx_list = []
        self.work = False
        self.on_off = 1
        self.dim = 0
        self.comp_list = np.zeros(3)

    def get(self, *args):
        output = []
        data = None
        n = len(args)
        for s in args:
            data = getattr(self, f'{s}')
            if isinstance(data, list):
                if isinstance(data[0], np.ndarray):
                    data = np.array(data)
            output.append(data.copy())
        if n == 1:
            return output[0]
        else:
            return output

    def update(self, prediction: Prediction):
        P = prediction.get('P')
        dim_P = P.shape[0]
        if self.work:
            R = self.on_off * self.R
            K = P @ self.H.T @ np.linalg.inv(self.H @ P @ self.H.T + R)
            # dx is always set to zero after compensation, so we can simplify the equation
            # self.dx = dx + K @ (self.Z - self.H @ dx)
            self.dx = K @ self.Z
            self.P = (np.eye(dim_P) - K @ self.H) @ P @ (np.eye(dim_P) - K @ self.H).T + K @ R @ K.T
            self.KH = K @ self.H
            prediction.renew(self.P)

            self.HK_list.append(np.diag(self.H @ K))
            self.P_list.append(np.diag(self.P.copy()))
            self.dx_list.append(self.dx.reshape(-1))
        else:
            self.dx = np.zeros((dim_P, 1))

    def compensate(self, ME: MechanizationEquation):
        if self.work:
            temp_dx = -np.reshape(self.dx, -1) * self.comp_list
        else:
            temp_dx = np.zeros(3)
        ME.qut.rotate(*temp_dx, 1)
        # if np.abs(self.Z[1, 0]) > np.deg2rad(10):
            #print(f"new:  {np.rad2deg(ME.qut.ori[:2])}")

    def record(self, time):
        self.time_list.append(time)
        self.Z_list.append(self.Z.reshape(-1))
        self.R_list.append(np.diag(self.on_off * self.R))

    def switch(self, on_off):
        if on_off:
            self.on_off = 1
        else:
            self.on_off = 1e3

    @staticmethod
    def filter(old, new, alpha):
        if isinstance(old, list):
            old_array = np.array(old)
            new_array = np.array(new)
        else:
            old_array = old
            new_array = new
        filtered_array = (1 - alpha) * old_array + alpha * new_array
        return filtered_array


class AccLevelingUpdate(Update):
    """this update need referenced pos, vel"""

    def __init__(self):
        super().__init__()
        self.std_omg = None
        self.std_acc = None
        self.dim = 2

    def set_init(self, std_imu):
        self.std_acc = np.array(std_imu[3:6])
        self.std_omg = np.array(std_imu[0:3])

    def input(self, acc, qut: Quaternion, time):
        if self.work:
            self.comp_list[:] = [1, 1, 0]

            self.gen_Z(acc, qut)
            self.gen_H()
            self.gen_R()

            self.record(time)

    def gen_Z(self, acc, qut):
        new_pr = AccLeveling(*acc)
        d_pr = qut.ori[0:2] - new_pr

        self.Z = np.reshape(d_pr, (-1, 1))

        if np.abs(qut.ori[0]) >= np.deg2rad(80):
            self.Z[0, 0] = 0
            self.comp_list[0] = 0

        # if np.abs(self.Z[1, 0]) > np.deg2rad(10):
        #     print("")
            # print(f"ori:  {np.rad2deg(qut.ori[0:2])}")
            # print(f"acc:  {np.rad2deg(new_pr)}")

    def gen_H(self):
        self.H = np.zeros((self.dim, 3))
        self.H[0, 0] = 1
        self.H[1, 1] = 1

    def gen_R(self):
        error_leveling = self.std_acc / 9.8
        self.R = np.diag([error_leveling[1], error_leveling[0]]) ** 2


def AccLeveling(fx, fy, fz, pos=None):
    """return [pitch, roll]"""
    pitch = np.arctan2(fy, (fx ** 2 + fz ** 2) ** 0.5)
    roll = np.arctan2(-fx, fz)

    return [pitch, roll]
