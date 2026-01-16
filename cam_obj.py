import numpy as np
import cv2
from picamera2 import Picamera2


class Camera:
    
    def __init__(self, tolerance=50):
        self.capture = Picamera2()
        self.video_config = self.capture.create_video_configuration(main={"size" : (640, 640), "format" : "BGR888"})
        self.capture.start()
        self.tolerance = tolerance
        self.width, self.height = self.capture.stream_configuration('main')['size']
        
    def _get_frame(self):
        frame = self.capture.capture_array()
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
    camera = Camera()
    
    while True:
        if cv2.waitKey(1) == 27:
            break
            
        frame, ball_pos = camera.detect_ball()
        cv2.rectangle(frame,
                (camera.width // 2 - camera.tolerance, camera.height // 2 + camera.tolerance),
                (camera.width // 2 + camera.tolerance, camera.height // 2 - camera.tolerance), (0, 0, 0), 5)
                
        if not isinstance(ball_pos, list):
            cv2.imshow('frame', frame)
            continue
            
        cv2.circle(frame, (ball_pos[0], ball_pos[1]), ball_pos[2], (255, 255, 255), 5)
        cv2.imshow('frame', frame)
