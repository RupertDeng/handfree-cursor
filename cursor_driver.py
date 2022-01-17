import pyautogui

pyautogui.FAILSAFE = False
class CursorDriver:

  def __init__(self, face_length_pixel_scale, base_nomove_zone, lateral_scaling=1, vertical_scaling=1):
    """
    The mouse cursor movement is controlled by pixel distance and direction of face center point, away from the initial base point.
    Similar to the analog stick or joystick, the further face_center point moves away from base point, the faster screen cursor will move.
    And the face_center pixel distance is normalized to the face length (from center of eye brow to chin).

    face_length_pixel_scale: the virtual pixel resolution of face length, which essentially controls the cursor speed.
    The more pixel resolution given to face length, the faster cursor will move at the same physical head movement.

    base_nomove_zone: pixel radius of the dead area at base point which will trigger no cursor movement.

    lateral_scaling, vertical_scaling: default to 1. if set larger than 1, cursor will move faster along x / y direction accordingly.
    """
    self.face_length_pixel_scale = face_length_pixel_scale
    self.base_nomove_zone = base_nomove_zone
    self.lateral_scaling = lateral_scaling
    self.vertical_scaling = vertical_scaling
    self.base_point = []
    self.init_length = 0

  def get_length(self, point1, point2):
    return int(((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5)

  def get_cursor_movement(self, face_center, face_length):
    dx = face_center[0] - self.base_point[0]
    dy = face_center[1] - self.base_point[1]
    normalization = self.init_length / face_length
    cursor_dx = int(dx * normalization * self.lateral_scaling)
    cursor_dy = int(dy * normalization * self.vertical_scaling)
    return cursor_dx, cursor_dy

  
  def steering(self, data_pipe):
    cursor_dx, cursor_dy = 0, 0
    while True:
      if data_pipe.poll():
        face_center, mouth_top, mouth_bottom, face_top, face_bottom = data_pipe.recv()
        if face_center[0] < 0: break

        if not self.base_point: self.base_point = face_center
        face_length = self.get_length(face_top, face_bottom)
        if not self.init_length: self.init_length = face_length

        if self.get_length(face_center, self.base_point) <= self.base_nomove_zone:
          cursor_dx = cursor_dy = 0
        else:
          cursor_dx, cursor_dy = self.get_cursor_movement(face_center, face_length)
      pyautogui.move(cursor_dx, cursor_dy)
    

