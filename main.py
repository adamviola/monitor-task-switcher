import alt_tab
import windows
import keyboard

# Create keyboard events
keyboard.add_hotkey('alt+tab', alt_tab.alt_tab, suppress=True)
keyboard.on_press_key('alt', alt_tab.alt_down)
keyboard.on_release_key('alt', alt_tab.alt_up)
    
# Hook into Windows events
windows.initialize()
