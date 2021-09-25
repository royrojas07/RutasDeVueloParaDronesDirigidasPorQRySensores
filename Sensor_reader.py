from grovepi import *
import grovepi
import time
ULTRASONIC_RANGER = 8
SOUND_SENSOR = A0
ULTRASONIC_RANGER_LED = 4
SOUND_SENSOR_LED = 3

class Sensor_reader:
    def __init__(self,sen_con_queue):
        self.sen_con_queue = sen_con_queue
    def start(distance_forward, distance_left, distance_right):
        while True:
            try:
                distance = ultrasonicRead(ultrasonic_ranger)
                loudness = analogRead(SOUND_SENSOR)
                print(distance,' cm')
                print("loudness = ", loudness)
                if distance <= 20 and loudness >= 800:
                    digitalWrite(ULTRASONIC_RANGER_LED,HIGH)
                    digitalWrite(SOUND_SENSOR_LED,HIGH)
                elif distance <= 20 and loudness < 800:
                    digitalWrite(ULTRASONIC_RANGER_LED,HIGH)
                    digitalWrite(SOUND_SENSOR_LED,LOW)
                elif distance >20 and loudness >= 800:
                    digitalWrite(ULTRASONIC_RANGER_LED,LOW)
                    digitalWrite(SOUND_SENSOR_LED,HIGH)
                else: 
                    digitalWrite(ULTRASONIC_RANGER_LED,LOW)
                    digitalWrite(SOUND_SENSOR_LED,LOW)
                time.sleep(.5)
            except IOError:
                print("Error")
    def send_command(self, command):
        self.sen_con_queue.put(command)