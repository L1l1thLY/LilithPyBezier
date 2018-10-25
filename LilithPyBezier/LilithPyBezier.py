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

        self.point = dict(Anchors=dict(xs=list(), ys=list()),
                          Bezier_points=dict(xs=list(), ys=list()))

        self.fig = plt.figure("Bezier", dpi=100, figsize=(length, width), frameon=False)
        self.canvas = self.fig.add_subplot(111)          # Fill the fig

        #self.canvas.set_axis('off')
        #self.canvas.gca().xaxis.set_major_locator(plt.NullLocator())
        #self.canvas.gca().yaxis.set_major_locator(plt.NullLocator())
        #self.canvas.adjust(top=1, bottom =0, right=1, left=0, hspace=0, wspace=0)
        #self.canvas.margins(0, 0)
        self._refresh_the_view()

        # ColorSetting
        self.bezier_line_color = 'k'
        self.bezier_dot_color = None
        self.anchor_line_color = None
        self.anchor_dot_color = None

        # Instance variables for GUI events loop
        self.pressed = None                    # Press tag, if press this value is 1
        self.picked = None                     # Pick tag, if picked some object this value is 1
        self.dragged = None                    # Drag tag, if moving the value is 1
        self.index_for_dragging = None
        self.closed = False
        self.tolerant = 10

    def show(self):
        self._binding()
        self.set_colors(bezier_line_color='r',
                        bezier_dot_color='b',
                        anchor_line_color='g',
                        anchor_dot_color='k')
        plt.show()

    def save_to_file(self, file_path):
        with open(file_path, mode='wb') as image_file:
            self.fig.savefig(image_file, format='png')

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
        self._bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])

    def _delete_point(self, mouse_location_x, mouse_location_y, tolerant):
        for index, point_location_x in enumerate(self.point['Anchors']['xs']):
            if abs(point_location_x - mouse_location_x) < tolerant and \
               abs(self.point['Anchors']['ys'][index] - mouse_location_y < tolerant):
                self.point['Anchors']['xs'].pop(index)
                self.point['Anchors']['ys'].pop(index)
                break
        self._bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])

    def delete_point_at_index(self, index):
        self.point['Anchors']['xs'].pop(index)
        self.point['Anchors']['ys'].pop(index)
        self._bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])

    def _replace_point(self, mouse_location_x, mouse_location_y, tolerant):
        _index = None
        for index, point_location_x in enumerate(self.point['Anchors']['xs']):
            if abs(point_location_x - mouse_location_x) < tolerant and \
               abs(self.point['Anchors']['ys'][index] - mouse_location_y < tolerant):
                self.point['Anchors']['xs'][index] = mouse_location_x
                self.point['Anchors']['ys'][index] = mouse_location_y
                return index
        self._bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])

    def replace_point_by_index(self, index, mouse_location_x, mouse_location_y):
        self.point['Anchors']['xs'][index] = mouse_location_x
        self.point['Anchors']['ys'][index] = mouse_location_y
        self._bezier(self.point['Anchors']['xs'], self.point['Anchors']['ys'])

    def _bezier(self, *args):
        t = np.linspace(0, 1)
        le = len(args[0]) - 1
        le_1 = 0
        b_x, b_y = 0, 0
        for x in args[0]:
            b_x = b_x + x * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)
            le = le - 1
            le_1 = le_1 + 1

        le = len(args[0]) - 1
        le_1 = 0
        for y in args[1]:
            b_y = b_y + y * (t ** le_1) * ((1 - t) ** le) * comb(len(args[0]) - 1, le_1)
            le = le - 1
            le_1 = le_1 + 1
        self.point['Bezier_points']['xs'] = b_x
        self.point['Bezier_points']['ys'] = b_y

    def get_anchors(self):
        return self.point['Anchors']

    def get_bezier_points(self):
        return self.point['Bezier_points']

    # Only for GUI closing trace
    def _is_the_first_anchor(self, mouse_location_x, mouse_location_y, tolerant):
        first_anchor_x = self.point['Anchors']['xs'][0]
        first_anchor_y = self.point['Anchors']['ys'][0]
        if abs(first_anchor_x - mouse_location_x) < tolerant and \
                abs(first_anchor_y - mouse_location_y < tolerant):
            return True
        else:
            return False

    # View
    def set_colors(self, bezier_line_color, bezier_dot_color, anchor_line_color, anchor_dot_color):
        self.bezier_line_color = bezier_line_color
        self.bezier_dot_color = bezier_dot_color
        self.anchor_line_color = anchor_line_color
        self.anchor_dot_color = anchor_dot_color

    def _refresh_the_view(self):
        self.canvas.clear()
        self.canvas.axis([1, 100 * self.length, 1, 100 * self.width])
        self.canvas.set_frame_on(False)
        self.canvas.set_axis_off()
        self.canvas.set_position([0, 0, 1, 1])

    def update_view(self, anchor_line=True, anchor_dot=True, bezier_line=True, bezier_dot=True):
        self._refresh_the_view()
        self._draw_bezier(bezier_line, bezier_dot)
        self._draw_anchor(anchor_line, anchor_dot)
        self.canvas.figure.canvas.draw()

    def _draw_bezier(self, plot=True, scatter=True):
        if plot is True:
            self.canvas.plot(self.point['Bezier_points']['xs'],
                             self.point['Bezier_points']['ys'],
                             color=self.bezier_line_color)
        if scatter is True:
            self.canvas.scatter(self.point['Bezier_points']['xs'],
                                self.point['Bezier_points']['ys'],
                                color=self.bezier_dot_color,
                                marker='o')

    def _draw_anchor(self, plot=True, scatter=True):
        if plot is True:
            self.canvas.plot(self.point['Anchors']['xs'],
                             self.point['Anchors']['ys'],
                             color=self.anchor_line_color)
        if scatter is True:
            self.canvas.scatter(self.point['Anchors']['xs'],
                                self.point['Anchors']['ys'],
                                color=self.anchor_dot_color,
                                marker='s',
                                picker=5)

    # Controller
    # events_loop: drag : press => pick => motion => release
    #              select : press => release
    # If u don't need GUI, please do not invoke any method here.

    def _binding(self):
        self.canvas.figure.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.figure.canvas.mpl_connect('pick_event', self._on_picker)

    def _event_loop_end(self):
        self.pressed = None
        self.picked = None
        self.dragged = None
        self.index_for_dragging = None

    def _on_press(self, event):
        if event.inaxes != self.canvas.axes:
            return

        self.pressed = 1

    def _on_release(self, event):
        if event.inaxes != self.canvas.axes:
            return

        # According to the event loop select : press => release
        if self.pressed is not None:
            self._select(event)

        self._event_loop_end()
        return

    def _on_motion(self, event):
        if event.inaxes != self.canvas.axes:
            return

        # According to the event loop drag : press => pick => motion => release
        if self.pressed is not None and self.picked is not None:
            self._drag(event)
        else:
            return

    def _on_picker(self, event):
        self.picked = 1

    def _select(self, event):
        # Selecting an exist point, it should be removed.
        if self.picked is not None and self.dragged is None:
            mouse_location_x = event.xdata
            mouse_location_y = event.ydata
            if self._is_the_first_anchor(mouse_location_x, mouse_location_y, self.tolerant) is True and \
               self.closed is False:
                self.add_anchor(self.point['Anchors']['xs'][0], self.point['Anchors']['ys'][0])
                self.closed = True
            elif self._is_the_first_anchor(mouse_location_x, mouse_location_y, self.tolerant) is True and self.closed is True:
                self.delete_point_at_index(0)
                self.delete_point_at_index(-1)
                self.closed = False
            else:
                self._delete_point(mouse_location_x, mouse_location_y, tolerant=self.tolerant)
        # Selecting an empty area, add a new point.
        elif self.dragged is None:
            self.add_anchor(event.xdata, event.ydata)
        self.update_view()

    def _drag(self, event):
        if self.dragged is None:
            self.dragged = 1
            if self._is_the_first_anchor(event.xdata, event.ydata, self.tolerant) is True and self.closed is True:
                self.dragged = 2
                self.replace_point_by_index(0, event.xdata, event.ydata)
                self.replace_point_by_index(-1, event.xdata, event.ydata)
            else:
                self.index_for_dragging = self._replace_point(event.xdata, event.ydata, self.tolerant)
        else:
            if self.dragged is 1:
                self.replace_point_by_index(self.index_for_dragging, event.xdata, event.ydata)
            else:
                self.replace_point_by_index(-1, event.xdata, event.ydata)
                self.replace_point_by_index(0, event.xdata, event.ydata)
        self.update_view()
