"""Direct window-scoped input for the user-authorized Cascadeur session.

Used because this session does not expose the bundled desktop-control runtime.
Each invocation takes one action and captures its resulting window state.
"""
import sys,ctypes,time,argparse
from ctypes import wintypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from PIL import ImageGrab
p=argparse.ArgumentParser();p.add_argument('action',choices=['observe','click','key','paste'])
p.add_argument('--window',type=int,required=True);p.add_argument('--x',type=int);p.add_argument('--y',type=int)
p.add_argument('--key');p.add_argument('--text');p.add_argument('--file');args=p.parse_args()
u=ctypes.windll.user32;k=ctypes.windll.kernel32
if args.window==0:
    def enum(h,l):
        b=ctypes.create_unicode_buffer(512);u.GetWindowTextW(h,b,512)
        pid=wintypes.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(pid))
        cp=wintypes.DWORD();u.GetWindowThreadProcessId(3147460,ctypes.byref(cp))
        if u.IsWindowVisible(h) and pid.value==cp.value:print(h,pid.value,b.value)
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(enum),0)
    sys.exit(0)
title=ctypes.create_unicode_buffer(512);u.GetWindowTextW(args.window,title,512)
target_pid=wintypes.DWORD();u.GetWindowThreadProcessId(args.window,ctypes.byref(target_pid))
parent_pid=wintypes.DWORD();u.GetWindowThreadProcessId(3147460,ctypes.byref(parent_pid))
if target_pid.value!=parent_pid.value or not u.IsWindowVisible(args.window):raise RuntimeError('Target is not a visible Cascadeur window')
foreground=u.GetForegroundWindow()
focus_target=u.GetLastActivePopup(args.window)
if not u.IsWindowVisible(focus_target):focus_target=args.window
foreground_thread=u.GetWindowThreadProcessId(foreground,None)
current_thread=k.GetCurrentThreadId()
u.AttachThreadInput(current_thread,foreground_thread,True)
try:
    u.BringWindowToTop(focus_target);u.SetForegroundWindow(focus_target)
finally:u.AttachThreadInput(current_thread,foreground_thread,False)
time.sleep(.2)
focused_pid=wintypes.DWORD();u.GetWindowThreadProcessId(u.GetForegroundWindow(),ctypes.byref(focused_pid))
if args.action!='observe' and focused_pid.value!=target_pid.value:raise RuntimeError('Cascadeur did not receive focus; input was not sent')
r=wintypes.RECT();u.GetWindowRect(args.window,ctypes.byref(r))
def key(v,up=False):
    u.keybd_event(v,0,2 if up else 0,0);time.sleep(.05)
def chord(keys):
    for v in keys:key(v)
    for v in reversed(keys):key(v,True)
if args.action=='click':
    u.SetCursorPos(r.left+args.x,r.top+args.y);time.sleep(.1);u.mouse_event(2,0,0,0,0);time.sleep(.1);u.mouse_event(4,0,0,0,0)
elif args.action=='key':
    names={'CTRL':17,'SHIFT':16,'ALT':18,'ENTER':13,'ESC':27,'TAB':9,'SPACE':32,'HOME':36,'END':35,'F5':116,'F6':117,'DELETE':46}
    chord([names[t] if t in names else ord(t.upper()) for t in args.key.split('+')])
elif args.action=='paste':
    text=Path(args.file).read_text() if args.file else args.text
    data=(text+'\0').encode('utf-16-le')
    k.GlobalAlloc.restype=wintypes.HGLOBAL;k.GlobalAlloc.argtypes=[wintypes.UINT,ctypes.c_size_t]
    k.GlobalLock.restype=ctypes.c_void_p;k.GlobalLock.argtypes=[wintypes.HGLOBAL]
    k.GlobalUnlock.argtypes=[wintypes.HGLOBAL]
    u.SetClipboardData.argtypes=[wintypes.UINT,wintypes.HANDLE];u.SetClipboardData.restype=wintypes.HANDLE
    if not u.OpenClipboard(args.window):raise RuntimeError('Clipboard unavailable')
    try:
        memory=k.GlobalAlloc(2,len(data));pointer=k.GlobalLock(memory);ctypes.memmove(pointer,data,len(data));k.GlobalUnlock(memory)
        u.EmptyClipboard()
        if not u.SetClipboardData(13,memory):raise RuntimeError('Clipboard write failed')
    finally:u.CloseClipboard()
    chord([17,86])
time.sleep(.6)
ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(ROOT/'Saved/Cascadeur/window.png')
print(title.value,'window',args.window,'action',args.action)
