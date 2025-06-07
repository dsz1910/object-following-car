from cam_obj import Camera
from car_obj import Car
from time import sleep
import cv2
import serial
import RPi.GPIO as gpio


ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1) # ewentualnie port = '/dev/ttyAMA0'
sleep(2)

camera = Camera(tolerance=50)
car = Car(speed=50)

while True:
    if cv2.waitKey(1) == 27:
        break
    
    frame, ball_pos = camera.detect_ball()
    cv2.rectangle(frame,
                (camera.width // 2 - camera.tolerance, camera.height // 2 + camera.tolerance),
                (camera.width // 2 + camera.tolerance, camera.height // 2 - camera.tolerance), (0, 0, 0), 5)
    
    if not isinstance(ball_pos, list):
        car.move('stop')
        cv2.imshow('frame', frame)
        continue
    
    direction = camera.decide_where_to_go(ball_pos)
    if direction == 'forward':
        distance = car.get_distance(ser, 'C')
        print(f'Centre distance: {distance}')
        
        if isinstance(distance, float) and distance < 25:
            left_dist = car.get_distance(ser, 'L')
            obstacle_dir = 'left' if isinstance(left_dist, float) and left_dist < 25 else 'right'
            print('Avoiding obstacle')
            car.avoid_obstacle(obstacle_dir, ser, distance, camera)
            direction = 'stop'
            
    print(f'Direction: {direction}')
    car.move(direction)
    
    
    cv2.circle(frame, (ball_pos[0], ball_pos[1]), ball_pos[2], (255, 255, 255), 5)
    cv2.imshow('frame', frame)


car.end_driving()
camera.close_windows()
gpio.cleanup()
