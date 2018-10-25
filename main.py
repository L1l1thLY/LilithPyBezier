from LilithPyBezier.LilithPyBezier import LPBezier
from PIL import Image

if __name__ == '__main__':
    newCanvas = LPBezier(6, 6) # which mean 6 * 100 px
    newCanvas.add_anchor(0, 0)
    newCanvas.add_anchor(340, 20)
    newCanvas.add_anchor(460, 46)
    newCanvas.add_anchor(600, 600)
    newCanvas.update_view(anchor_dot=False, anchor_line=False, bezier_line=True, bezier_dot=False)
    newCanvas.save_to_file("new.png")