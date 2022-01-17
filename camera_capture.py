import cv2
import dlib
import time

class CameraCapture:

  def __init__(self, cam_ind, cap_width, cap_height, cap_delay):
    """
    cam_ind: the index of camera to be used for face detection, typically "0".

    cap_width: camera capture width. 640 is a good starting point. 
    cap_height: camera capture height. 480 is a good starting point.
    Some cameras might experience numbers mismatching with actual resolution: https://stackoverflow.com/questions/19448078/python-opencv-access-webcam-maximum-resolution

    cap_delay: delay time between each capturing frame.
    The main purposes are 1) to ease CPU load on face detection. 2) to limit data input from this camera capture module to cursor driver module, due to bandwidth of inter-process communication.
    """
    self.capture = cv2.VideoCapture(cam_ind, cv2.CAP_DSHOW)   # CAP_DSHOW and CAP_MSMF are Windows backends for video capture.
    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
    self.cap_delay = cap_delay
    self.detector = dlib.get_frontal_face_detector()
    self.predictor = dlib.shape_predictor('shape_68.dat')

  def destruct(self):
    """
    Clean up and release resource whenever needed.
    """
    self.capture.release()
    cv2.destroyAllWindows()

  def get_face(self, frame):
    """
    Face detection from video capture frame. Only allow one face to be there.
    Returns a flag for 3 possible scenarios, the detected face object, as well as converted grayscale frame picture.
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = self.detector(gray_frame, 1)
    if len(faces) == 0:
      return 0, None, None
    if len(faces) > 1:
      return 2, None, None
    face = faces.pop()
    return 1, face, gray_frame

  def get_key_points(self, gray_frame, face):
    """
    Extract 5 key points from the detected face.
    """
    landmarks = self.predictor(gray_frame, face)
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

  def draw_key_points(self, frame, points, base):
    """
    Draw the key points onto the video capture frame if needed.
    """
    cv2.circle(frame, base, 25, (200, 200, 200), -1)
    for x, y in points:
      cv2.circle(frame, (x, y), 5, (0, 255, 255), -1)
    

  def streaming(self, data_pipe, show_key_points):
    """
    The final function to capture frame, detect face, extract key points and send over to cursor driver process.
    Ends the while loop if 'q' key is pressed.

    data_pipe: the inter-process communication pipe object.
    show_key_points: boolean parameter whether or not to show the 5 extracted key points.
    """
    END = [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]    # End signal to send over to end the cursor driver process
    base_point = []                                             # the first face_center point as base_point
    while True:
      success, frame = self.capture.read()
      frame = cv2.flip(frame, 1)
      if not success:
        self.destruct()
        data_pipe.send(END)
        raise Exception('Camera capturing failed!')
      
      flag, face, gray_frame = self.get_face(frame)
      if flag == 0:
        continue
      elif flag == 2:
        self.destruct()
        data_pipe.send(END)
        raise Exception('More than one faces are detected!')
      
      key_points = self.get_key_points(gray_frame, face)
      data_pipe.send(key_points)
      if not base_point: base_point = key_points[0]
      if show_key_points: self.draw_key_points(frame, key_points, base_point)
      cv2.imshow('Face', frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        self.destruct()
        data_pipe.send(END)
        break
      if self.cap_delay > 0: time.sleep(self.cap_delay)

  



      

    





