from screeninfo import get_monitors

monitors = []

# Returns the index of the monitor containing the provided point
def monitor_of_point(x, y):
    for i, monitor in enumerate(monitors):
        if x >= monitor[0][0] and  x < monitor[0][1] \
            and y >= monitor[1][0] and  y < monitor[1][1]:
            return i

# Stores monitor dimensions
def update_monitors():
    ms = get_monitors()
    monitors.clear()
    for m in ms:
        monitors.append(((m.x, m.x + m.width), (m.y, m.y + m.height)))

update_monitors()