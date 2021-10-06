from djitellopy import Tello
from threading import Thread
from time import sleep
import queue
import sys
from Controller import *
from ImageCaption import *

dron = Tello()
dron.connect()
cam_con_queue = queue.Queue() #cola entre la camara y el controlador
sen_con_queue = queue.Queue() #cola entre el sensor y el controlador
max_height = sys.argv[1]

def main():
    threads = [Thread( target=init_Controller, args=()),
               Thread( target=init_camera, args=()),
               Thread( target=init_sensor, args=())]

    for thread in threads:
        thread.start()
    

def init_Controller():
    controller = Controller(dron,cam_con_queue,sen_con_queue)
    controller.thread_init()

def init_camera():
    imageCaption = ImageCaption(dron,cam_con_queue,max_height)
    imageCaption.thread_init()

def init_sensor():
    print("hilo de sensor")

if __name__ == '__main__':
	main()