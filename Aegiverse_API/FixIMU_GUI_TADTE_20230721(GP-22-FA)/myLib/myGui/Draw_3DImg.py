import datetime
import sys

import numpy as np
from OpenGL.GL.shaders import compileProgram
from OpenGL.raw.GLUT import glutInitDisplayMode, GLUT_SINGLE, GLUT_RGBA, GLUT_ALPHA
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import glutInit, glutDisplayFunc, glutIdleFunc
from OpenGL.raw.GLU import gluLookAt, gluPerspective
from Quaternion import *
from AttitudeReference import *


class openGL_Widget_Cube(QOpenGLWidget):
    update_GLImg_qt = pyqtSignal(bool)
    def __init__(self, parent=None):
        super(openGL_Widget_Cube, self).__init__(parent)
        self.vertices_rectangle_right = []
        self.vertices_rectangle_left = []
        self.vertices_rectangle_top = []
        self.vertices_rectangle_middle = []
        #self.Quaternion = Quaternion(0, 0, 0)
        self.AR = AR()
        # self.x_angle = 20
        # self.y_angle = 35
        # self.z_angle = 15
        self.x_Axis = 0
        self.y_Axis = 0
        self.z_Axis = 0
        self.x_acc = 0
        self.y_acc = 0
        self.z_acc = 0
        self.time = 0
        # self.x_angle = 0
        # self.y_angle = 0
        # self.z_angle = 0
        self.main()


    def initGL(self):
        vertices = []

        self.vertices_rectangle_right = [
            [-0.5, 0.5, 0.25],  # front
            [-1.0, -0.5, 0.25],
            [-0.5, -0.5, 0.25],
            [0.0, 0.5, 0.25],
            [-0.5, 0.5, -0.25],  # left
            [-1.0, -0.5, -0.25],
            [-1.0, -0.5, 0.25],
            [-0.5, 0.5, 0.25],
            [0.0, 0.5, 0.25],  # right
            [-0.5, -0.5, 0.25],
            [-0.5, -0.5, -0.25],
            [0.0, 0.5, -0.25],
            [0.0, 0.5, -0.25],  # behind
            [-0.5, -0.5, -0.25],
            [-1.0, -0.5, -0.25],
            [-0.5, 0.5, -0.25],
            [-0.5, 0.5, -0.25],  # top
            [-0.5, 0.5, 0.25],
            [0.0, 0.5, 0.25],
            [0.0, 0.5, -0.25],
            [-1.0, -0.5, -0.25],  # botton
            [-1.0, -0.5, 0.25],
            [-0.5, -0.5, 0.25],
            [-0.5, -0.5, -0.25],
        ]

        self.vertices_rectangle_left = [
            [0.0, 0.5, 0.25],  # front
            [0.5, -0.5, 0.25],
            [1.0, -0.5, 0.25],
            [0.5, 0.5, 0.25],
            [0.0, 0.5, -0.25],  # left
            [0.5, -0.5, -0.25],
            [0.5, -0.5, 0.25],
            [0.0, 0.5, 0.25],
            [0.5, 0.5, 0.25],  # right
            [1.0, -0.5, 0.25],
            [1.0, -0.5, -0.25],
            [0.5, 0.5, -0.25],
            [0.5, 0.5, -0.25],  # behind
            [1.0, -0.5, -0.25],
            [0.5, -0.5, -0.25],
            [0.0, 0.5, -0.25],
            [0.0, 0.5, -0.25],  # top
            [0.0, 0.5, 0.25],
            [0.5, 0.5, 0.25],
            [0.5, 0.5, -0.25],
            [0.5, -0.5, -0.25],  # botton
            [0.5, -0.5, 0.25],
            [1.0, -0.5, 0.25],
            [1.0, -0.5, -0.25],
        ]

        self.vertices_rectangle_top = [
            [-0.2, 1.0, 0.25],  # front
            [-0.5, 0.5, 0.25],
            [0.5, 0.5, 0.25],
            [0.2, 1.0, 0.25],
            [-0.2, 1.0, -0.25],  # left
            [-0.5, 0.5, -0.25],
            [-0.5, 0.5, 0.25],
            [-0.2, 1.0, 0.25],
            [0.2, 1.0, 0.25],  # right
            [0.5, 0.5, 0.25],
            [0.5, 0.5, -0.25],
            [0.2, 1.0, -0.25],
            [0.2, 1.0, -0.25],  # behind
            [0.5, 0.5, -0.25],
            [-0.5, 0.5, -0.25],
            [-0.2, 1.0, -0.25],
            [-0.2, 1.0, -0.25],  # top
            [-0.2, 1.0, 0.25],
            [0.2, 1.0, 0.25],
            [0.2, 1.0, -0.25],
            #[-0.5, 0.5, -0.25],  # botton
            # [-0.2, 1.0, 0.25],
            # [0.5, 0.5, 0.25],
            # [0.5, 0.5, -0.25],
        ]

        self.vertices_rectangle_middle = [
            [-0.2, 0.1, 0.25],  # front
            [-0.3, -0.1, 0.25],
            [0.3, -0.1, 0.25],
            [0.2, 0.1, 0.25],
            # [-0.3, 0.1, -0.25],  # left
            # [-0.4, -0.1, -0.25],
            # [-0.4, -0.1, 0.25],
            # [-0.3, 0.1, 0.25],
            # [0.3, 0.1, 0.25],  # right
            # [0.4, -0.1, 0.25],
            # [0.4, -0.1, -0.25],
            # [0.3, 0.1, -0.25],
            [0.2, 0.1, -0.25],  # behind
            [0.3, -0.1, -0.25],
            [-0.3, -0.1, -0.25],
            [-0.2, 0.1, -0.25],
            [-0.2, 0.1, -0.25],  # top
            [-0.2, 0.1, 0.25],
            [0.2, 0.1, 0.25],
            [0.2, 0.1, -0.25],
            [-0.3, -0.1, -0.25],  # botton
            [-0.3, -0.1, 0.25],
            [0.3, -0.1, 0.25],
            [0.3, -0.1, -0.25],
        ]

        #self.vertices = np.array(vertices, dtype=np.float32)


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #glViewport(0, 0, 400, 300)
        gluPerspective(45, float(300) / 200, 0.1, 50.0)
        # gluLookAt(-1, 35, 10, 5, 5, 5, 0, 0, 1)  # 設定視角和相機位置
        gluLookAt(0, 0, -4, 0, 0.5, 0, 0, 1, 0)
        #gluLookAt(0, 0, -5, -1, 0.5, 0.5, 0, 1, 0)
        #
        # self.angle += 20
        # if self.angle > 360:
        #     self.angle = 45
        # glRotatef(self.angle, 10, 5, 0)
        #glRotatef(self.angle, 0, 0, 0)

        glPushMatrix()
        # glBegin(GL_TEXTURE_2D)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # self.x_angle += self.x_Axis
        # self.y_angle += self.y_Axis
        # self.z_angle += self.z_Axis
        # if self.x_angle > 360:
        #     self.x_angle = self.x_angle - 360
        # if self.y_angle > 360:
        #     self.y_angle = self.y_angle - 360
        # if self.z_angle > 360:
        #     self.z_angle = self.z_angle - 360
        # glRotatef(self.x_angle, 1.0, 0.0, 0.0)
        # glRotatef(self.y_angle, 0.0, 1.0, 0.0)
        # glRotatef(self.z_angle,0.0, 0.0, 1.0)

        # self.Quaternion.rotate(self.x_Axis, self.y_Axis, self.z_Axis)
        # Axis_arr = self.Quaternion.getRotationArray()
        Omega = np.deg2rad([self.x_Axis, self.y_Axis, self.z_Axis])
        acc = np.array([self.x_acc, self.y_acc, self.z_acc])
        #mSec = datetime.datetime.now().microsecond
        self.AR.update(self.time, Omega, acc)
        #print(np.rad2deg(self.Quaternion.orientation))
        Axis_arr = self.AR.getRotationArray()
        glRotatef(Axis_arr[0], Axis_arr[2], Axis_arr[3], Axis_arr[1])
        # print(acc)
        # print(Omega)
        # x_angle = random.randint(0, 360)
        # y_angle = random.randint(0, 360)
        # z_angle = random.randint(0, 360)
        # glRotatef(x_angle, 3.0, 0.0, 0.0)
        # glRotatef(y_angle, 0.0, 5.0, 0.0)
        # glRotatef(z_angle,0.0, 0.0, 7.0)

        # glBegin(GL_LINES)
        # for f in self.faces:
        #     for vertex_idx in f:
        #         x, y, z = self.vertices[vertex_idx[0] - 1]
        #         glVertex3f(x, y, z)
        # glEnd()

        # glBegin(GL_TRIANGLES)
        # for f in self.faces:
        #     for vertex_idx, normal_idx, texcoord_idx in f:
        #         x, y, z = self.vertices[vertex_idx - 1]
        #         glVertex3f(x, y, z)
        #
        # glEnd()
        #glutWireTeapot(0.5)

        glColor3f(0.7058823529411765,0.7098039215686275,0.8745098039215686)
        glEnableClientState(GL_VERTEX_ARRAY)
        #glEnableClientState(GL_NORMAL_ARRAY)


        # glVertexPointer(3, GL_FLOAT, 0, self.vertices_Cube)
        # glDrawArrays(GL_QUADS, 0, len(self.vertices_Cube))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_right)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_right))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_left)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_left))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_top)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_top))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_middle)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_middle))
        #glNormalPointer(GL_FLOAT, 0, self.normals)

        #glDrawElements(GL_TRIANGLES, len(self.faces), GL_UNSIGNED_INT, self.faces)




        #glDrawArrays(GL_QUADS, 1, len(self.vertices))
        #glDrawArrays(GL_LINES, 0, len(self.faces)//3)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1.0, 1.0, 1.0)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_right)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_right))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_left)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_left))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_top)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_top))

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_rectangle_middle)
        glDrawArrays(GL_QUADS, 0, len(self.vertices_rectangle_middle))

        glDisableClientState(GL_VERTEX_ARRAY)

        #glDisableClientState(GL_NORMAL_ARRAY)
        glPopMatrix()

        glFlush()

    def main(self):
        glutInit()
        self.initGL()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA | GLUT_ALPHA)
        glutDisplayFunc(self.paintGL)
        glutIdleFunc(self.paintGL)

    def update_GL(self):
        self.update()

    def resetDraw(self):
        self.AR.me.qut=Quaternion(0, 0, 0)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget_win = openGL_Widget_Cube()
    widget_win.show()
    sys.exit(app.exec_())