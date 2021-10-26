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
        self.sen_con_queue.get()
        self.sen_con_queue.put(command)
    
    def guide_drone(self,drone_distance):
        if(drone_distance <= self.landing_distance):
            distance_forward = self.landing_distance - drone_distance
            print("se manda instruccion para que vaya para adelante " + str(distance_forward))
            #self.send_command("F:" + str(distance_forward))
            self.dron.move_forward(distance_forward)
            print("va a aterrizar")
        elif(drone_distance > self.landing):
            distance_backward = drone_distance - self.landing_distance
            self.dron.move_backward(distance_backward)
    
    def land_drone(self):
        self.send_command("LAND")
    
    def lookforsensors(self):
        drone_height = self.dron.get_height()
        if(drone_height > self.sensor_height):
            distance = drone_height - self.sensor_height
            if(distance >= 20):
                #self.send_command("D:"+str(distance))
                self.dron.move_down(distance)
            else:
                temp = 20+distance
                if(drone_height + 20 <= self.max_height ):
                    #self.send_command("U:20")
                    #self.send_command("D:"+str(temp))
                    self.dron.move_up(20)
                    self.dron.move_down(temp)
        elif(drone_height < self.sensor_height):
            distance = self.sensor_height - drone_height 
            if(distance >= 20):
                #self.send_command("U:"+str(distance))
                self.dron.move_up(distance)
            else:
                temp = 20+distance
                if(drone_height - 20 > 0):
                    self.dron.move_down(20)
                    self.dron.move_up(temp)
                    #self.send_command("D:20")
                    #self.send_command("U:"+str(temp))

    def routine(self):
        print("[INFO] SensorReader: Waiting for message from Controller")
        self.log.print("INFO","SensorReader","Waiting for message from Controller")
        self.sen_con_queue.get()
        print("[INFO] SensorReader: Message received from Controller")
        self.log.print("INFO","SensorReader","Message received from Controller")
        self.sen_con_queue.put("LOOKING")
        print("[INFO] SensorReader: Sensors looking for drone")
        self.log.print("INFO","SensorReader","Sensors looking for drone")
        drone_distance = self.start() #se trata de detectar el dron y cuando se detecta se guia
        self.guide_drone(drone_distance) #se guia el dron hacia el punto de aterrizaje
        self.land_drone() #se aterriza el dron
    
    def start(self):
        ultrasonic_detected = False
        sound_detected = False
        drone_not_detected = True
        drone_distance_from_sensor = 0
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
                    dronoe_distance_from_sensor = distance
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
                print("Sensor error")
            except TypeError:
                print("Sensor error") 
            if(ultrasonic_detected and sound_detected):
                print("Drone detected")
                drone_not_detected = False
                digitalWrite(ULTRASONIC_RANGER_LED,0)
                digitalWrite(SOUND_SENSOR_LED,0)
            else:
                self.lookforsensors()
        return drone_distance_from_sensor

