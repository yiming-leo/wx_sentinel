import win32api
import win32gui
import win32con


def switch_to_english_keyboard():
    """
    切换输入法到美式键盘 (ENG)
    """
    # 输入法代码 '00000409' 代表 美式英语键盘
    ENGLISH_KEYBOARD_CODE = '00000409'

    try:
        # 获取当前前台窗口的句柄
        hwnd = win32gui.GetForegroundWindow()
        # 加载英文键盘布局
        hkl = win32api.LoadKeyboardLayout(ENGLISH_KEYBOARD_CODE, win32con.KLF_ACTIVATE)
        # 向目标窗口发送切换输入法的消息
        win32api.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, hkl)
        print("✅ 输入法已切换到英文键盘")
    except Exception as e:
        print(f"❌ 输入法切换失败: {e}")