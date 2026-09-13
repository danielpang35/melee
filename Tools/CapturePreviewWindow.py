"""Read-only capture of the explicitly selected Unreal preview process."""
import ctypes,sys,time
from ctypes import wintypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from PIL import ImageGrab
pid=int(sys.argv[1]);tag=sys.argv[2]
if not tag.replace('_','').isalnum():raise ValueError('Invalid capture tag')
u=ctypes.windll.user32;windows=[]
def enum(h,l):
    p=wintypes.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==pid:
        t=ctypes.create_unicode_buffer(512);u.GetWindowTextW(h,t,512)
        print('Observed preview window',h,t.value)
        if t.value.startswith('MeleeCombatLab ('):windows.append((h,t.value))
    return True
u.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(enum),0)
if len(windows)!=1:raise RuntimeError(str(windows))
h,title=windows[0];u.ShowWindow(h,9);u.SetForegroundWindow(h);time.sleep(.3)
r=wintypes.RECT();u.GetWindowRect(h,ctypes.byref(r))
for frame in range(4):
    ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(ROOT/f'Saved/Cascadeur/{tag}_{frame}.png')
    time.sleep(.4)
print(pid,title,tag)
