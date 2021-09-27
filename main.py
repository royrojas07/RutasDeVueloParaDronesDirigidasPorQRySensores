from djitellopy import Tello
from threading import Thread
from time import sleep
import queue
from Controller import *

#dron = Tello()
#dron.connect()
dron = "hola"
cam_con_queue = queue.Queue() #cola entre la camara y el controlador
sen_con_queue = queue.Queue() #cola entre el sensor y el controlador

def main():
    threads = [Thread( target=init_Controller, args=()),
               Thread( target=init_camera, args=()),
               Thread( target=init_sensor, args=())]

    for thread in threads:
        thread.start()
    

def init_Controller():
    controller = Controller(dron,cam_con_queue,sen_con_queue)
    controller.start_processing()

def init_camera():
    print("hilo de camara")
    sleep(5)
    cam_con_queue.put("U:30,RR:20")


def init_sensor():
    print("hilo de sensor")

if __name__ == '__main__':
	main()