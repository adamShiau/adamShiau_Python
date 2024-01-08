import numpy as np
import myLib.myKM.transformation as tf


def AccLeveling(fx, fy, fz, pos=None):
    """return [pitch, roll]"""
    if pos == 1:
        f = np.array([fx, fy, fz]) / 9.8
        pitch = np.arcsin(np.clip(fy, -1, 1))

    elif pos is not None:
        # coarse alignment with position
        g0 = tf.gravity(pos)
        a = fy / g0
        if a < -1 or a > 1:
            a = np.clip(a, -1, 1)
        pitch = np.arcsin(a)
    else:
        # coarse alignment without position
        pitch = np.arctan2(fy, (fx ** 2 + fz ** 2) ** 0.5)

    roll = np.arctan2(-fx, fz)

    return [pitch, roll]


def gyrocompassing(wx, wy, wz, roll, pitch):
    # 由地球自轉推算yaw
    yaw = np.arctan2((wx * np.cos(roll) + wz * np.sin(roll)),
                     (wy * np.cos(pitch) + wx * np.sin(pitch) * np.sin(roll)
                      - wz * np.cos(roll) * np.sin(pitch)))
    # 近似公式 yaw = np.arctan(wx/wy)
    return yaw
