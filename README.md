# A simple Windows application for hands-free mouse-cursor control

## 1) Basic mechanism:
- Two processes are running in parallel utilizing multi-core CPU.
- `Camera-capture` process will detect key face landmark points using opencv and dlib pre-trained ML model in real time, and send the data over to cursor-control process.
- `Cursor process` will listen to the data flow and calculate cursor movement based on how far face-center point is away from original position (much like an analog stick), and drive cursor via pyautogui package. This is considerably faster than the face recognication so a separate process can avoid cursor jittering due to waiting for data.

## 2) Some consideration for user experience:
- All pixel distances are `normalized to face length` so no major difference in response when face is further or closer to camera.
- A `non-move center dead zone` is defined so when face center point is within the zone, cursor will not move. This helps stop the cursor quickly and also filter out small face wobbling near center location.
- `Mouth opening/closing can control cursor movement speed`. Higher speed when mouth is open and slower when closed. This can make targeting small screen object easier while keeping overall agility.
- When face-center is in the non-move zone, `mouse single click can be performed by opening and closing mouth once`. It works nicely on all apps even when the camera window is not on top.

## 3) Installation and Testing
- Install the required packages after cloning the repository
- Download the pre-trained 68-point dlib model from [this link](https://github.com/davisking/dlib-models/blob/master/shape_predictor_68_face_landmarks.dat.bz2). Extract the dat file, rename to 'shape_68.dat' and save under root.
- Start the app with `python main.py`, terminate it by press 'q' on the camera window.
- Play with the provided parameters for camera and cursor modules to suit your preference.
- Extend the functionality as you like and have fun.