import numpy as np
from myLib.myKM.transformation import Quaternion
import myLib.myKM.transformation as tf


class MechanizationEquation:
    def __init__(self):
        self.pre_time = 0
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
        self.qut = Quaternion(0, 0, 0)
        self.pre_acc = np.zeros(3)
        self.pre_acc[2] = 9.8
        self.pre_omg = np.zeros(3)

    def setInit(self, time=None, pos=None, vel=None, qut=None, pre_acc=None, pre_omg=None):
        if time is not None:
            self.pre_time = time
        if pos is not None:
            self.pos = pos
        if vel is not None:
            self.vel = vel
        if qut is not None:
            self.qut = Quaternion(qut)
        if pre_acc is not None:
            self.pre_acc = pre_acc
        if pre_omg is not None:
            self.pre_omg = pre_omg


class AttitudeReference(MechanizationEquation):
    def __init__(self):
        super().__init__()

    def update(self, dt, omg):
        # dt = time - self.pre_time
        self.qut.rotate(*omg, dt)
        # self.pre_time = time
        self.pre_omg = omg.copy()
