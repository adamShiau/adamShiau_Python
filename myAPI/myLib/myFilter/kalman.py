class kalman_1D:

    def __init__(self, x0=0, p0=0, Q=1, R=1):
        self.__x = x0
        self.__p = p0
        self.__kal_Q = Q
        self.__kal_R = R
        print("init Q = ", self.kal_Q)
        print("init R = ", self.kal_R)

    @property
    def kal_Q(self):
        return self.__kal_Q

    @kal_Q.setter
    def kal_Q(self, Q):
        self.__kal_Q = Q
        print("set kal_Q = ", Q)

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        print("set kal_R = ", R)

    def update(self, z):
        k = self.__p / (self.__p + self.__kal_R)
        x = self.__x + k * (z - self.__x)
        p = (1 - k) * self.__p
        self.predict(x, p)
        return x, p

    def predict(self, x, p):
        self.__x = x
        self.__p = p + self.__kal_Q
