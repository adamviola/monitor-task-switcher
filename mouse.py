from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def mouse_position():
    pos = POINT()
    windll.user32.GetCursorPos(byref(pos))
    return (pos.x, pos.y)