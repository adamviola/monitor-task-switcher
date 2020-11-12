from counter import Counter
from monitors import monitor_of_point, monitors
from mouse import mouse_position
from windows import activate_window

alt_tabs = Counter()

# Triggered when alt is first pressed down
def alt_down(e):
    alt_tabs.reset()
    print('alt')

# Triggered when alt+tab hotkey is pressed
def alt_tab():
    alt_tabs.increment()

# Triggered when alt is released
def alt_up(e):
    idx = int(alt_tabs)
    if idx == 0:
        return

    cursor_pos = mouse_position()
    monitor = monitor_of_point(cursor_pos[0], cursor_pos[1])
    activate_window(idx, monitor)

    alt_tabs.reset()

