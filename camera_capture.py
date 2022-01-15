import cv2
import dlib
import time

class CameraCapture:

  def __init__(self, cam_ind, cap_width, cap_height, cap_delay):
    self.capture = cv2.VideoCapture(cam_ind, cv2.CAP_DSHOW)
    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
    self.cap_delay = cap_delay
    self.detector = dlib.get_frontal_face_detector()
    self.predictor = dlib.shape_predictor('shape_68.dat')

  def destruct(self):
    self.capture.release()
    cv2.destroyAllWindows()

  def get_face(self, frame):
    frame = cv2.flip(frame, 1)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = self.detector(gray_frame, 1)
    if len(faces) == 0:
      return 0, None, None
    if len(faces) > 1:
      return 2, None, None
    face = faces.pop()
    return 1, face, gray_frame

  def get_key_points(self, gray_frame, face):
    landmarks = self.detector(gray_frame, face)
    face_top = [21, 22]
    face_bottom = [7, 8, 9]
    face_center = [32, 33, 34]
    mouth_top = [61, 62, 63]
    mouth_bottom = [65, 66, 67]
    areas = [face_center, mouth_top, mouth_bottom, face_top, face_bottom]
    points = []
    for area in areas:
      point_x = sum(landmarks.part(i).x for i in area) // len(area)
      point_y = sum(landmarks.part(i).y for i in area) // len(area)
      points.append((point_x, point_y))
    return points

  def draw_key_points(self, frame, points):
    for x, y in points:
      cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)


  def streaming(self, data_pipe, show_key_points):
    END = [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]
    while True:
      success, frame = self.capture.read()
      if not success:
        self.destruct()
        data_pipe.send(END)
        raise Exception('Camera capturing failed!')
      
      flag, face, gray_frame = self.get_face(self, frame)
      if flag == 0:
        continue
      elif flag == 2:
        self.destruct()
        data_pipe.send(END)
        raise Exception('More than one faces are detected!')
      
      key_points = self.get_key_points(gray_frame, face)
      data_pipe.send(key_points)
      if show_key_points: self.draw_key_points(frame, key_points)
      cv2.imshow('Face', frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        data_pipe.send(END)
        break
      time.sleep(self.cap_delay)

  



      

    





