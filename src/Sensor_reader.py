from grovepi import *
import grovepi
import time
import numpy as np
from threading import Thread

ULTRASONIC_RANGER = 8
SOUND_SENSOR = 0
ULTRASONIC_RANGER_LED = 4
SOUND_SENSOR_LED = 3

class Sensor_reader:
    def __init__(self,dron,sen_con_queue,landing_distance,max_height,sensor_height,log):
        self.dron = dron
        self.sen_con_queue = sen_con_queue
        self.landing_distance = landing_distance
        self.sensor_height = sensor_height
        self.max_height = max_height
        self.src_thread = Thread( target=self.routine, args=() )
        self.log = log

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
            distance_forward = self.landing_distance - mean_distance
            self.send_command("F:" + distance_forward)
        else:
            self.send_command("SENSOR ERROR")

    def land_drone(self):
        self.dron.land()
    
    def lookforsensors(self):
        drone_height = self.dron.get_height()
        if(drone_height > self.sensor_height):
            distance = drone_height - self.sensor_height
            if(distance >= 20):
                self.send_command("D:"+distance)
            else:
                temp = 20+distance
                if(drone_height + 20 <= self.max_height ):
                    self.send_command("U:20")
                    self.send_command("D:"+temp)
        elif(drone_height < self.sensor_height):
            distance = self.sensor_height - drone_height 
            if(distance >= 20):
                self.send_command("U:"+distance)
            else:
                temp = 20+distance
                if(drone_height - 20 > 0):
                    self.send_command("D:20")
                    self.send_command("U:"+temp)

    def routine(self):
        exit_thread = False
        land = False
        while not exit_thread and not land:
            print("[INFO] SensorReader: Waiting for message from Controller")
            self.log.print("INFO","SensorReader","Waiting for message from Controller")
            self.sen_con_queue.get()
            print("[INFO] SensorReader: Message received from Controller")
            self.log.print("INFO","SensorReader","Message received from Controller")
            self.start() #se trata de detectar el dron y cuando se detecta se guia
            self.guide_drone()
            self.land_drone() #falta implementar metodo
    
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
                if distance <= 100 and loudness >= 150:
                    digitalWrite(ULTRASONIC_RANGER_LED,1)
                    digitalWrite(SOUND_SENSOR_LED,1)
                    ultrasonic_detected = True
                    sound_detected = True
                elif distance <= 100 and loudness < 150:
                    digitalWrite(ULTRASONIC_RANGER_LED,1)
                    digitalWrite(SOUND_SENSOR_LED,0)
                elif distance > 100 and loudness >= 150:
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
            else:
                lookforsensors()

