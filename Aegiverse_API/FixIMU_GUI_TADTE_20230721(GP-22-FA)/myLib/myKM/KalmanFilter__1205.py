import numpy as np
from numpy import cos, sin, tan
from myLib.myKM.Attitude_Alignment import AccLeveling
from myLib.myKM.transformation import Quaternion
from myLib.myKM.MechanizationEquation import MechanizationEquation


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

    def renew(self, P: np.ndarray):
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


class EKF(Prediction):
    def __init__(self):
        super().__init__()
        self.var_omg = None
        self.P = np.eye(4)
        self.pre_time = None
        self.gen_F()
        self.qut = Quaternion(0, 0, 0)
        self.AccLeveling_update = AccLevelingUpdate()
        self.AccLeveling_update.work = True
        self.bias = np.zeros(3)

    def run(self, dt, omg, acc):
        self.gen_Q(dt)
        self.gen_F(dt)
        self.qut.rotate(*(omg - self.bias), dt)
        self.predict()
        if np.abs(np.sum(acc ** 2) ** 0.5 - 1) < 0.02 and np.abs(self.qut.ori[0]) < np.deg2rad(45) and np.abs(self.qut.ori[1]) < np.deg2rad(45):
            self.AccLeveling_update.input(acc, self.qut.ori)
            self.AccLeveling_update.update(self)
            self.AccLeveling_update.compensate(self)
            print("111")

    def setInit(self, std_imu):
        self.var_omg = np.diag([*std_imu[:3]]) ** 2
        self.AccLeveling_update.set_init(std_imu)

    def gen_F(self, dt=0.01):
        """state transition matrix"""
        A = np.zeros((4, 4))
        A[2:4, 2:4] = -np.eye(2, 2)
        self.F = np.eye(4) + A * dt

    def gen_Q(self, dt=0.01):
        """可能需要再調整"""
        ro_mat = self.qut.R_b2l
        G = np.zeros((4, 3))
        G[0:2] = ro_mat[:2]
        G[2:4, 0:2] = np.eye(2)
        self.Q = self.F @ G @ self.var_omg @ G.T @ self.F.T * dt


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
        self.comp_list = None

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
            ME.qut.rotate(temp_dx[0], temp_dx[1], 0, 1)

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
        self.std_acc = None
        self.dim = 2
        self.comp_list = np.array([1, 1, 1, 1])

    def set_init(self, std_imu):
        self.std_acc = np.array(std_imu[3:6])

    def input(self, acc, ori):
        if self.work:
            # self.comp_list[:] = 1

            self.gen_Z(acc, ori)
            self.gen_H()
            self.gen_R()

    def gen_Z(self, acc, ori):
        new_pr = AccLeveling(*acc)
        d_pr = ori[0:2] - new_pr
        self.Z = np.reshape(d_pr, (-1, 1))

    def gen_H(self):
        self.H = np.zeros((2, 4))
        self.H[0:2, 0:2] = np.eye(2)

    def gen_R(self, acc=None):
        if acc is not None:
            s_fx, s_fy, s_fz = self.std_acc ** 2
            fx, fy, fz = acc ** 2
            self.R = np.zeros((2, 2))
            self.R[0, 0] = fx * s_fz / (fx + fz) ** 2 + fz * s_fx / (fx + fz) ** 2
            self.R[1, 1] = fx * fy * s_fx / ((fx + fz) * (fy + (fx + fz)) ** 2) + \
                           fy * fz * s_fz / ((fx + fz) * (fy + (fx + fz)) ** 2) + \
                           s_fy * (fx + fz) / (fy + (fx + fz)) ** 2

        else:
            error_leveling = self.std_acc / 9.8
            self.R = np.diag([error_leveling[1], error_leveling[0]]) ** 2

    def compensate(self, predictor: EKF):
        if self.work:
            temp_dx = -np.reshape(self.dx, -1) * self.comp_list
            predictor.qut.rotate(temp_dx[0], temp_dx[1], 0, 1)
            predictor.bias[0:2] -= temp_dx[2:4]


class MagUpdate(Update):
    def __init__(self):
        super().__init__()
        self.std_mag = None
        self.dim = 1
        self.comp_list = np.eye(1)

    def set_init(self, std_mag):
        self.std_mag = np.array(std_mag)

    def input(self, mag, tilt, time):
        if self.work:
            self.gen_Z(mag, tilt)
            self.gen_H(mag, tilt)
            self.gen_R()

            self.record(time)

    def gen_Z(self, mag, tilt):
        mx, my, mz = mag
        pitch, roll = tilt
        new_mx = mx * np.cos(roll) + mz * np.sin(roll)
        new_my = mx * np.sin(pitch) * np.sin(roll) + my * np.cos(pitch) - mz * np.sin(pitch) * np.cos(roll)
        yaw = -np.tan2(new_mx, new_my)
        self.Z = np.reshape([yaw], (-1, 1))

    def gen_H(self):
        self.H = np.eye(1)

    def gen_R(self, mag=None, tilt=None):
        if tilt is not None:
            mx, my, mz = mag
            s_x, s_y, s_z = self.std_mag ** 2
            pitch, roll = tilt
            self.R = np.empty((1, 1))
            self.R[0, 0] = s_x ** 2 * ((-mx * cos(roll) - mz * sin(roll)) * sin(pitch) * sin(roll) / (
                    (mx * cos(roll) + mz * sin(roll)) ** 2 + (
                    mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(pitch) * cos(roll)) ** 2) + (
                                               mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(
                                           pitch) * cos(roll)) * cos(roll) / (
                                               (mx * cos(roll) + mz * sin(roll)) ** 2 + (
                                               mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(
                                           pitch) * cos(roll)) ** 2)) ** 2 + s_y ** 2 * (
                                   -mx * cos(roll) - mz * sin(roll)) ** 2 * cos(pitch) ** 2 / (
                                   (mx * cos(roll) + mz * sin(roll)) ** 2 + (
                                   mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(pitch) * cos(
                               roll)) ** 2) ** 2 + s_z ** 2 * (
                                   -(-mx * cos(roll) - mz * sin(roll)) * sin(pitch) * cos(roll) / (
                                   (mx * cos(roll) + mz * sin(roll)) ** 2 + (
                                   mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(pitch) * cos(
                               roll)) ** 2) + (mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(
                               pitch) * cos(roll)) * sin(roll) / ((mx * cos(roll) + mz * sin(roll)) ** 2 + (
                                   mx * sin(pitch) * sin(roll) + my * cos(pitch) - mz * sin(pitch) * cos(
                               roll)) ** 2)) ** 2


class UKF:
    def __init__(self):
        self.Z = None
        self.L = 2
        self.LD = 1
        self.W = None
        self.P = np.zeros((self.L, self.L))
        self.Q = np.zeros((self.L, self.L))
        self.R = np.zeros((self.L, self.L))
        self.dx = np.zeros(self.L)
        self.F = np.eye(2)
        self.H = np.eye(2)
        self.var_imu = None

    def setInit(self, std_imu):
        self.var_imu = std_imu ** 2

    def filter(self, dt, acc, qut: Quaternion):
        self.gen_Q(qut, dt)
        self.gen_Z(acc, qut)
        self.gen_R(acc)
        self.calculate()

    def calculate(self):
        self.dx = np.zeros(self.L)

        # calculate sigma points
        A = np.linalg.cholesky((self.LD + self.L) * self.P)
        sigma_points = [self.dx]
        for i in range(self.L):
            sigma_points.append(A[i, :])
            sigma_points.append(-A[i, :])

        # calculate weight
        self.W = [self.LD / (self.L + self.LD)]
        for i in range(2 * self.L):
            self.W.append(self.LD / (self.L + self.LD) / 2)

        sigma_points = np.array(sigma_points)
        self.W = np.array(self.W)

        # predict status
        predict_sigma_point = (self.F @ sigma_points.T).T
        X_ = np.zeros(self.L)
        for i in range(2 * self.L + 1):
            X_ += self.W[i] * predict_sigma_point[i]

        dif_x = predict_sigma_point - X_
        P_ = self.Q.copy()
        for i in range(2 * self.L + 1):
            P_ += self.W[i] * np.outer(dif_x[i], dif_x[i])

        # predict measurement
        H = np.eye(2)
        Y = (H @ predict_sigma_point.T).T
        Y_ = np.zeros(self.L)
        for i in range(2 * self.L):
            Y_ += self.W[i] * Y[i]

        dif_z = predict_sigma_point - X_
        Pyy = self.R.copy()
        for i in range(2 * self.L + 1):
            Pyy += self.W[i] * np.outer(dif_z[i], dif_z[i])

        Pxy = np.zeros((2, 2))
        for i in range(2 * self.L + 1):
            Pxy += self.W[i] * np.outer(dif_x[i], dif_z[i])

        # measurement update
        K = Pxy @ np.linalg.inv(Pyy)
        self.dx = X_ + K @ (self.Z - Y_)
        self.P = P_ - K @ Pyy @ K.T

    def gen_Q(self, qut: Quaternion, dt=0.01):
        """可能需要再調整"""
        ro_mat = qut.R_b2l
        G = ro_mat[:2]
        self.Q = self.F @ G @ self.var_imu[0:3] @ G.T @ self.F.T * dt

    def gen_Z(self, acc, qut):
        new_pr = AccLeveling(*acc)
        d_pr = qut.ori[0:2] - new_pr
        self.Z = np.reshape(d_pr, (-1, 1))

    def gen_R(self, acc=None):
        var_acc = self.var_imu[3:6]
        if acc is not None:
            s_fx, s_fy, s_fz = var_acc
            fx, fy, fz = acc ** 2
            self.R = np.zeros((2, 2))
            self.R[0, 0] = fx * s_fz / (fx + fz) ** 2 + fz * s_fx / (fx + fz) ** 2
            self.R[1, 1] = fx * fy * s_fx / ((fx + fz) * (fy + (fx + fz)) ** 2) + \
                           fy * fz * s_fz / ((fx + fz) * (fy + (fx + fz)) ** 2) + \
                           s_fy * (fx + fz) / (fy + (fx + fz)) ** 2

        else:
            error_leveling = var_acc / 9.8 ** 2
            self.R = np.diag([error_leveling[1], error_leveling[0]])
