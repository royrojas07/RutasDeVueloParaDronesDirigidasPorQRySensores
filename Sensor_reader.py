from grovepi import *
import grovepi
import time
ULTRASONIC_RANGER = 8
SOUND_SENSOR = 0
ULTRASONIC_RANGER_LED = 4
SOUND_SENSOR_LED = 3

class Sensor_reader:
    def __init__(self,sen_con_queue,landing_distance):
        self.sen_con_queue = sen_con_queue
        self.landing_distance = landing_distance
    
    def send_command(self, command):
        self.sen_con_queue.put(command)
    
    def guide_drone(self):
        distance = ultrasonicRead(ULTRASONIC_RANGER)
        if(distance < self.landing_distance):
            send_command(self,20)
    
    def start():
        ultrasonic_detected = False
        sound_detected = False
        drone_not_detected = True
        while drone_not_detected:
            try:
                distance = ultrasonicRead(ULTRASONIC_RANGER)
                loudness = analogRead(SOUND_SENSOR)
                print(distance,' cm')
                print("loudness = ", loudness)
                if distance <= 20 and loudness >= 150:
                    digitalWrite(ULTRASONIC_RANGER_LED,1)
                    digitalWrite(SOUND_SENSOR_LED,1)
                    ultrasonic_detected = False
                    sound_detected = False
                elif distance <= 20 and loudness < 150:
                    digitalWrite(ULTRASONIC_RANGER_LED,1)
                    digitalWrite(SOUND_SENSOR_LED,0)
                elif distance >20 and loudness >= 150:
                    digitalWrite(ULTRASONIC_RANGER_LED,0)
                    digitalWrite(SOUND_SENSOR_LED,1)
                else: 
                    digitalWrite(ULTRASONIC_RANGER_LED,0)
                    digitalWrite(SOUND_SENSOR_LED,0)
                time.sleep(.5)
            except IOError:
                print("Error")
            if(ultrasonic_detected and sound_detected):
                print("Drone detected")
                drone_not_detected = False
        guide_drone(self)
