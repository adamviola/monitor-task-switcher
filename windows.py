# Edited https://gist.github.com/keturn/6695625

import sys
import ctypes
import ctypes.wintypes
from monitors import monitor_of_point, monitors

hwnd_info = {}
windows = [[] for monitor in monitors]

# Windows-related constants
user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

CONST_SW_SHOW = 5
WINEVENT_OUTOFCONTEXT = 0x0000
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOPMOST = 0x00000008
WS_VISIBLE = 0x10000000
WS_MINIMIZE = 0x20000000

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_SYSTEM_MINIMIZEEND = 0x0017
EVENT_SYSTEM_MOVESIZEEND = 0x000B

events = [EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_MINIMIZEEND, EVENT_SYSTEM_MOVESIZEEND]

def activate_window(idx, monitor):
    cleaned_windows = []
    for hwnd in windows[monitor]:
        if is_valid(hwnd):
            cleaned_windows.append(hwnd)
    
    windows[monitor] = cleaned_windows

    hwnd = cleaned_windows[-(idx % len(cleaned_windows) + 1)]

    # Workaround for SetForegroundWindow()
    windowThreadProcessId = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(),0)
    currentThreadId = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(windowThreadProcessId, currentThreadId, True)
    user32.BringWindowToTop(hwnd)
    user32.ShowWindow(hwnd, CONST_SW_SHOW)
    user32.AttachThreadInput(windowThreadProcessId,currentThreadId, False)


def set_monitor(hwnd, checked=False):
    if not checked and not is_alt_tab(hwnd):
        return
    
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))

    prev_monitor = None
    if 'monitor' in hwnd_info[hwnd]:
        prev_monitor = hwnd_info[hwnd]['monitor']

    monitor = monitor_of_point((rect.left + rect.right) / 2, (rect.top + rect.bottom) / 2)
    hwnd_info[hwnd]['monitor'] = monitor

    if prev_monitor is not None:
        windows[prev_monitor].remove(hwnd)
        windows[monitor].append(hwnd)

    return monitor


def is_valid(hwnd):
    # Check if it is a window via isWindow and then check if exe is same?
    return user32.IsWindow(hwnd)

def is_alt_tab(hwnd):
    style = user32.GetWindowLongW(hwnd, -16)
    ext_style = user32.GetWindowLongW(hwnd, -20)

    if ext_style & WS_EX_APPWINDOW != 0:
        return True

    if style & WS_MINIMIZE != 0 or ext_style & WS_EX_TOPMOST != 0:
        return False

    return user32.GetAncestor(hwnd, 2) == hwnd and user32.GetWindow(hwnd, 4) == 0

def window_focused(hwnd):
    if not is_alt_tab(hwnd):
        return

    if hwnd in hwnd_info:
        monitor = hwnd_info[hwnd]['monitor']
        windows[monitor].remove(hwnd)
    else:
        hwnd_info[hwnd] = {}
        monitor = set_monitor(hwnd, checked=True)
    
    windows[monitor].append(hwnd)

def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime): 
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)

    title = title.value
    if event == EVENT_SYSTEM_MOVESIZEEND:
        set_monitor(hwnd)
    else:
        window_focused(hwnd)


# Hooks onto specified event
def setHook(WinEventProc, eventType):
    return user32.SetWinEventHook(
        eventType,
        eventType,
        0,
        WinEventProc,
        0,
        0,
        WINEVENT_OUTOFCONTEXT
    )

def initialize():
    # Initialization
    ole32.CoInitialize(0)

    # Specify callback
    WinEventProc = WinEventProcType(callback)
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

    # Hooks on to the the specified events
    hookIDs = [setHook(WinEventProc, ev) for ev in events]
    if not any(hookIDs):
        print('SetWinEventHook failed')
        sys.exit(1)

    # Wait for events 
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    # Clean up
    for hookID in hookIDs:
        user32.UnhookWinEvent(hookID)
    ole32.CoUninitialize()
