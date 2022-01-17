import pyautogui

pyautogui.FAILSAFE = False
class CursorDriver:

  def __init__(self, face_length_pixel_scale, base_nomove_zone, lateral_scaling, vertical_scaling, mouth_open_thresh, speed_limiter_factor):
    """
    The mouse cursor movement is controlled by pixel distance and direction of face center point, away from the initial base point.
    Similar to the analog stick or joystick, the further face_center point moves away from base point, the faster screen cursor will move.
    And the face_center pixel distance is normalized to the face length (from center of eye brow to chin).

    face_length_pixel_scale: the virtual pixel resolution of face length, which essentially controls the cursor speed.
    The more pixel resolution given to face length, the faster cursor will move at the same physical head movement.

    base_nomove_zone: pixel radius of the dead area at base point which will trigger no cursor movement.
    lateral_scaling, vertical_scaling: default to 1. if set larger than 1, cursor will move faster along x / y direction accordingly.

    mouth_open_thresh: pixel thresh to detect that mouth is open
    speed_limiter_factor: no speed limiter when mouth is open, otherwise, the speed_limiter_factor is applied to reduce cursor speed
    """
    self.face_length_pixel_scale = face_length_pixel_scale
    self.base_nomove_zone = base_nomove_zone
    self.lateral_scaling = lateral_scaling
    self.vertical_scaling = vertical_scaling
    self.mouth_open_thresh = mouth_open_thresh
    self.speed_limiter_factor = speed_limiter_factor
    self.base_point = []
    self.init_length = 0
    self.mouth_sequence = []

  def get_length(self, point1, point2):
    return int(((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5)

  def get_cursor_movement(self, face_center, mouth_opening, normalization):
    """
    get cursor x/y step by normalizing the distance between face center point and base point.
    if mouth is closed, speed limiter will apply.
    """
    dx = face_center[0] - self.base_point[0]
    dy = face_center[1] - self.base_point[1]
    opening = mouth_opening * normalization
    limiter = 1 if opening >= self.mouth_open_thresh else self.speed_limiter_factor
    cursor_dx = int(dx * normalization * self.lateral_scaling * limiter)
    cursor_dy = int(dy * normalization * self.vertical_scaling * limiter)
    return cursor_dx, cursor_dy

  def detect_click(self, mouth_opening, normalization):
    """
    detect the single click event by mouth open and close, when face_center is within the base nomove zone.
    """
    is_open = (mouth_opening * normalization) >= self.mouth_open_thresh
    if not self.mouth_sequence:
      if not is_open:
        self.mouth_sequence.append(is_open)
    else:
      if self.mouth_sequence[-1] != is_open:
        self.mouth_sequence.append(is_open)
      if len(self.mouth_sequence) == 3:
        pyautogui.click()
        self.mouth_sequence = []

  
  def steering(self, data_pipe):
    """
    steering the mouse cursor based on input data from camera capture via data_pipe
    if negative data received, ends the while loop
    """
    cursor_dx, cursor_dy = 0, 0
    while True:
      if data_pipe.poll():    # if not data received (due to slow face detection), keep using previous dx, dy without waiting
        face_center, mouth_top, mouth_bottom, face_top, face_bottom = data_pipe.recv()
        if face_center[0] < 0: break

        # assign the first frame data as the initial parameters for base center point and face length
        if not self.base_point: self.base_point = face_center
        face_length = self.get_length(face_top, face_bottom)
        if not self.init_length: self.init_length = face_length

        mouth_opening = self.get_length(mouth_top, mouth_bottom)
        normalization = face_length / self.init_length
        if self.get_length(face_center, self.base_point) <= self.base_nomove_zone:
          cursor_dx = cursor_dy = 0
          self.detect_click(mouth_opening, normalization)
        else:
          if self.mouth_sequence: self.mouth_sequence = []
          cursor_dx, cursor_dy = self.get_cursor_movement(face_center, mouth_opening, normalization)

      pyautogui.move(cursor_dx, cursor_dy)
    

