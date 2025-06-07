import numpy as np
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep


class Camera:
    
    def __init__(self, tolerance=50):
        self.capture = PiCamera()
        self.capture.resolution = (640, 480)
        self.capture.framerate = 60
        self.raw_capture = PiRGBArray(self.capture, size=(640, 480))
        self.width, self.height = self.capture.resolution
        self.tolerance = tolerance
        sleep(0.1)
        
    def _get_frame(self):
        self.raw_capture.truncate(0)
        self.capture.capture(self.raw_capture, format='bgr')
        frame = self.raw_capture.array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (15, 15), 0)
        return frame
    
    def detect_ball(self):
        frame = self._get_frame()
        
        balls = cv2.HoughCircles(
            frame,
            cv2.HOUGH_GRADIENT,
            dp=1.3,
            minDist=100,
            param1=100,
            param2=60,
            minRadius=5,
            maxRadius=200
        )
        
        if isinstance(balls, np.ndarray):
            balls = np.uint16(np.round(balls))
            return frame, [balls[0,0,0], balls[0, 0, 1], balls[0, 0, 2]] # frame,  [x, y, z]
        return frame, None
    
    def decide_where_to_go(self, ball_pos):
        if self.width // 2 + self.tolerance < ball_pos[0]:
            return 'right'
        if self.width // 2 - self.tolerance > ball_pos[0]:
            return 'left'
        if self.height // 2 + self.tolerance < ball_pos[1]:
            return 'back'
        if self.height // 2 - self.tolerance > ball_pos[1]:
            return 'forward'
        return 'stop'
    
    @staticmethod
    def close_windows():
        cv2.destroyAllWindows()
        
if __name__ == '__main__':
    cam = Camera()
    
    while True:
        if cv2.waitKey(1) == 27:
            break
            
        frame = cam._get_frame()
        cv2.imshow('frame', frame)
            
        

