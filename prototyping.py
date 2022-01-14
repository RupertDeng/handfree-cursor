import cv2
import dlib
import pyautogui
from multiprocessing import Process, Pipe
import time


def camera_input(conn):
  capture = cv2.VideoCapture(0)
  cap_width, cap_height = 480, 640
  detector = dlib.get_frontal_face_detector()
  predictor = dlib.shape_predictor('shape_68.dat')
  center_x, center_y = 0, 0

  while True:
    success, frame = capture.read()
    frame = cv2.flip(frame, 1)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame, 1)
    if len(faces) >= 1: Exception('More than one face are detected')
    for face in faces:
      landmarks = predictor(gray_frame, face)
      x, y = landmarks.part(33).x, landmarks.part(33).y
      if not center_x or not center_y: center_x, center_y = x, y
      conn.send((x-center_x, y-center_y))
      # cursor_dx, cursor_dy = (x - center_x) * 3, (y - center_y) * 3
      # pyautogui.move(cursor_dx, cursor_dy)
      cv2.circle(gray_frame, (x, y), 2, (0, 0, 255), 1)
    cv2.imshow('Face', gray_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      conn.send((1920, 0))
      break
    time.sleep(0.2)
  capture.release()
  cv2.destroyAllWindows()

def cursor_driver(conn):
  cursor_dx, cursor_dy = 0, 0
  while True:
    if conn.poll():
      cursor_dx, cursor_dy = conn.recv()
      if cursor_dx == 1920: break
    pyautogui.move(cursor_dx, cursor_dy)

if __name__ == '__main__':
  # camera_input()
  downstream_conn, upstream_conn = Pipe(False)
  camera_process = Process(target=camera_input, args=(upstream_conn,))
  cursor_process = Process(target=cursor_driver, args=(downstream_conn,))
  camera_process.start()
  cursor_process.start()
  camera_process.join()
  cursor_process.join()

