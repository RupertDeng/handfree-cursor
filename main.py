from multiprocessing import Process, Pipe
from camera_capture import CameraCapture
from cursor_driver import CursorDriver

def camera(conn):
  camera_instance = CameraCapture(0, 640, 480, 0)   # cam_ind, cap_width, cap_height, cap_delay
  camera_instance.streaming(conn, True)    # data_pipe, show_key_points

def cursor(conn):
  cursor_instance = CursorDriver(1000, 25, 2, 2.4, 8, 0.15) # face_length_pixel_scale, base_nomove_zone, lateral_scaling, vertical_scaling, mouth_open_thresh, speed_limiter_factor
  cursor_instance.steering(conn)   # data_pipe


if __name__ == '__main__':

  # create inter-process communication data pipe, and create the camera and cursor processes respectively
  downstream_conn, upstream_conn = Pipe(False)
  camera_process = Process(target=camera, args=(upstream_conn,))
  cursor_process = Process(target=cursor, args=(downstream_conn,))

  # start both processes. they will be terminated if key "q" is pressed on the camera window.
  camera_process.start()
  cursor_process.start()
  camera_process.join()
  cursor_process.join()

