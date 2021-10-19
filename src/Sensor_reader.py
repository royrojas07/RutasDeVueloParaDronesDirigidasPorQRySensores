#from grovepi import *
#import grovepi
import time
import numpy as np

ULTRASONIC_RANGER = 8
SOUND_SENSOR = 0
ULTRASONIC_RANGER_LED = 4
SOUND_SENSOR_LED = 3

class Sensor_reader:
    def __init__(self,sen_con_queue,landing_distance):
        self.sen_con_queue = sen_con_queue
        self.landing_distance = landing_distance

    def thread_init(self):
        self.src_thread.start()
    
    def send_command(self, command):
        self.sen_con_queue.put(command)
    
    def guide_drone(self):
        distances = []
        for i in range(6):
            distances.append(ultrasonicRead(ULTRASONIC_RANGER))
        mean_distance = np.mean(distances)
        if(distance <= self.landing_distance and self.sen_con_queue.get() == "END" or self.sen_con_queue.get() == "NEXT"):
            self.send_command(self, "F " + self.landing_distance - mean_distance)

    def start(self):
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
                    ultrasonic_detected = True
                    sound_detected = True
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
        self.guide_drone(self)
