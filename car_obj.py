import RPi.GPIO as gpio
from RPi.GPIO import OUT, HIGH, LOW
from time import sleep
from statistics import median
import serial


gpio.setmode(gpio.BCM)

class Car:
    
    def __init__(self, freq=1000, speed=50):
        self.in1 = 17
        self.in2 = 22
        self.ena = 27
        self.in3 = 18
        self.in4 = 23
        self.enb = 24
        self.obstacle_avoiding_velocity = 45.5
        
        gpio.setup(self.in1, OUT)
        gpio.setup(self.in2, OUT)
        gpio.setup(self.ena, OUT)
        gpio.setup(self.in3, OUT)
        gpio.setup(self.in4, OUT)
        gpio.setup(self.enb, OUT)
        
        self.pwm_a = gpio.PWM(self.ena, freq)
        self.pwm_b = gpio.PWM(self.enb, freq)
        self.pwm_a.start(speed)
        self.pwm_b.start(speed)
    
    def _stop_motors(self):
        gpio.output(self.in1, LOW)
        gpio.output(self.in2, LOW)
        gpio.output(self.in3, LOW)
        gpio.output(self.in4, LOW)
    
    def _move_backwards(self):
        self._stop_motors()
        self.change_speed(70)
        gpio.output(self.in1, HIGH)
        gpio.output(self.in3, HIGH)
        
    def _move_right(self):
        self._stop_motors()
        self.change_speed(40)
        gpio.output(self.in3, HIGH)
        
    def _move_left(self):
        self._stop_motors()
        self.change_speed(40)
        gpio.output(self.in1, HIGH)
        
    def _move_forward(self):
        self._stop_motors()
        self.change_speed(70)
        gpio.output(self.in2, HIGH)
        gpio.output(self.in4, HIGH)

    def move(self, direction):
        directions = {'left' : self._move_left, 'right' : self._move_right,
                      'forward' : self._move_forward, 'back' : self._move_backwards, 'stop' : self._stop_motors}
        directions[direction]()
        
    def change_speed(self, speed):
        self.pwm_a.ChangeDutyCycle(speed)
        self.pwm_b.ChangeDutyCycle(speed)
        
    def end_driving(self):
        self._stop_motors()
        self.pwm_a.stop()
        self.pwm_b.stop()
    
    def calculate_time(self, dist):
        return (dist / self.obstacle_avoiding_velocity ) + 0.5
		
    @staticmethod
    def get_distance(ser, sensor):
        dist = []
        ser.reset_input_buffer()
        
        for _ in range(4):
            ser.write(sensor.encode())
            ser.flush()
                
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    dist.append(float(line))
                except:
                    pass
        if dist:
                return median(dist)
        return 2137666
        
    def avoid_obstacle(self, obstacle_dir, ser, obstacle_dist, camera):
        self.move('stop')
        move_dir_order = ('right', 'left') if obstacle_dir == 'left' else ('left', 'right')
        self.move(move_dir_order[0])
        
        while True:
            dist = self.get_distance(ser, 'C')
            if isinstance(dist, float) and dist > 25:
                break
        
        self.move('stop')
        calculated_time = self.calculate_time(obstacle_dist)
        self.move('forward')
        sleep(calculated_time)
        self.move('stop')
        
        self.find_the_object(camera, move_dir_order[1])
        
    def find_the_object(self, camera, direction='left'):
        self.move(direction)
		
        while True:
            if camera.detect_ball()[1] is not None:
                break
		
        self.move('stop')


if __name__ == '__main__':
    try:
        car = Car(speed=100, freq=1000)
        ser = serial.Serial('/dev/serial0', baudrate=9600)
        sleep(5)
        for _ in range(5):
                dist = car.get_distance(ser, 'L')
                print(dist)
        
    except:
        pass
    finally:
        gpio.cleanup()
