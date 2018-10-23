from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from scipy.special import comb
import io


class LPBezier(object):
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.point = dict(Anchors=dict(xs=list(), ys=list()), Control_points=dict(xs=None, ys=None))
        self.fig = plt.figure("Bezier", dpi=100, figsize=(length, width), frameon=False)
        self.fig.suptitle("LilithPyBezier")
        self.canvas = self.fig.add_subplot(111)
        # ViewControllerDelegate
        self.pressed = None                   # Press tag, if press this value is 1
        self.picked = None                    # Pick tag, if picked some object this value is 1
        self.dragged = None                    # Drag tag, if moving the value is 1
        self.index_for_dragging = None

        self.cidpress = self.canvas.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.canvas.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.canvas.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidpick = self.canvas.figure.canvas.mpl_connect('pick_event', self.on_picker)

    @staticmethod
    def debug_print(arg):
        print(arg)

    @staticmethod
    def show():
        plt.show()

    # TODO: Should update it to photoshop version
    def add_control_point(self, x, y, anchor_id=id):
        pass

    # TODO: Should update it to photoshop version
    def get_matrix(self):
        _buffer = io.BytesIO()
        self.fig.savefig(_buffer, format='png')
        pillow_data = Image.open(_buffer)
        binary_data = pillow_data.convert('1')
        np_matrix = np.asarray(binary_data)
        binary_data.show()
        _buffer.close()

        return np_matrix

    # Model
    def add_anchor(self, x, y):
        self.point['Anchors']['xs'].append(x)
        self.point['Anchors']['ys'].append(y)

    def delete_point(self, mouse_location_x, mouse_location_y, tolerant):
        for index, point_location_x in enumerate(self.point['Anchors']['xs']):
            if abs(point_location_x - mouse_location_x) < tolerant and \
               abs(self.point['Anchors']['ys'][index] - mouse_location_y < tolerant):
                self.point['Anchors']['xs'].pop(index)
                self.point['Anchors']['ys'].pop(index)
                break

    def replace_point(self, mouse_location_x, mouse_location_y, tolerant):
        _index = None
        for index, point_location_x in enumerate(self.point['Anchors']['xs']):
            if abs(point_location_x - mouse_location_x) < tolerant and \
               abs(self.point['Anchors']['ys'][index] - mouse_location_y < tolerant):
                self.point['Anchors']['xs'][index] = mouse_location_x
                self.point['Anchors']['ys'][index] = mouse_location_y
                return index

    def replace_point_by_index(self, index, mouse_location_x, mouse_location_y):
        self.point['Anchors']['xs'][index] = mouse_location_x
        self.point['Anchors']['ys'][index] = mouse_location_y

    # View
    def update_view(self):
        self.canvas.clear()
        self.canvas.axis([0, 1, 0, 1])
        self.draw_bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])
        self.draw_anchor()
        self.canvas.figure.canvas.draw()

    def draw_bezier(self, *args):  # Bezier曲线公式转换，获取x和y
        t = np.linspace(0, 1)  # t 范围0到1
        le = len(args[0]) - 1
        le_1 = 0
        b_x, b_y = 0, 0
        for x in args[0]:
            b_x = b_x + x * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)  # comb 组合，perm 排列
            le = le - 1
            le_1 = le_1 + 1

        le = len(args[0]) - 1
        le_1 = 0
        for y in args[1]:
            b_y = b_y + y * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)
            le = le - 1
            le_1 = le_1 + 1
        self.canvas.plot(b_x, b_y)

    def draw_anchor(self):
        self.canvas.scatter(self.point['Anchors']['xs'], self.point['Anchors']['ys'], color='k', marker='s', picker=5)
        self.canvas.plot(self.point['Anchors']['xs'], self.point['Anchors']['ys'])


    # Controller
    # event_loop: drag : press => pick => motion => release
    #             select : press => release
    def event_loop_end(self):
        self.pressed = None
        self.picked = None
        self.dragged = None
        self.index_for_dragging = None

    def on_press(self, event):
        if event.inaxes != self.canvas.axes:
            return

        self.pressed = 1

    def on_release(self, event):
        if event.inaxes != self.canvas.axes:
            return

        # According to the event loop select : press => release
        if self.pressed is not None:
            self.select(event)

        self.event_loop_end()
        return

    def on_motion(self, event):
        if event.inaxes != self.canvas.axes:
            return

        # According to the event loop drag : press => pick => motion => release
        if self.pressed is not None and self.picked is not None:
            self.drag(event)
        else:
            return

    def on_picker(self, event):
        self.debug_print("pick")
        self.picked = 1

    def select(self, event):
        # Selecting an exist point, it should be removed.
        if self.picked is not None and self.dragged is None:
            mouse_location_x = event.xdata
            mouse_location_y = event.ydata
            self.delete_point(mouse_location_x, mouse_location_y, tolerant=0.02)
        # Selecting an empty area, add a new point.
        elif self.dragged is None:
            self.add_anchor(event.xdata, event.ydata)
        self.update_view()

    def drag(self, event):
        if self.dragged is None:
            self.dragged = 1
            self.index_for_dragging = self.replace_point(event.xdata, event.ydata, 0.02)
        self.replace_point_by_index(self.index_for_dragging, event.xdata, event.ydata)
        self.update_view()




if __name__ == '__main__':
    newBezier = LPBezier(5, 5)
    newBezier.show()

    print("Hello")
