import pyautogui

screen_width, screen_height = pyautogui.size()
cursor_x, cursor_y = pyautogui.position()

pyautogui.moveTo(100, 150)
