from multiprocessing import Process, Pipe
from camera_capture import CameraCapture
from cursor_driver import CursorDriver


def camera(conn):
  camera_instance = CameraCapture(0, 640, 480, 0)
  camera_instance.streaming(conn, True)

def cursor(conn):
  cursor_instance = CursorDriver(1000, 30, 1.5, 1.5)
  cursor_instance.steering(conn)


if __name__ == '__main__':
  downstream_conn, upstream_conn = Pipe(False)
  camera_process = Process(target=camera, args=(upstream_conn,))
  cursor_process = Process(target=cursor, args=(downstream_conn,))
  camera_process.start()
  cursor_process.start()
  camera_process.join()
  cursor_process.join()

