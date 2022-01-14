import pyautogui
from multiprocessing import Process, Pipe

screen_width, screen_height = pyautogui.size()
# cursor_x, cursor_y = pyautogui.position()

# pyautogui.moveTo(100, 150)



def test(conn):
  while True:
    try:
      x, y = conn.recv()
    except EOFError:
      pass
    pyautogui.moveTo(x, y)
    x += 50
    if x >= 1920: break


if __name__ == '__main__':
  parent, child = Pipe(False)
  p = Process(target = test, args=(parent,))
  p.start()
  for x in range(0, 1920, 50):
    child.send((x, 300))
  p.join()

