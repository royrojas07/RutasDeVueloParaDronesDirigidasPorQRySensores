from djitellopy import Tello
import threading
from time import sleep
import queue
import sys
import signal
from Controller import *
from ImageCaption import *

dron = Tello()
dron.connect()
exit_event = threading.Event()
cam_con_queue = queue.Queue() #cola entre la camara y el controlador
sen_con_queue = queue.Queue() #cola entre el sensor y el controlador
max_height = int(sys.argv[1])
#print( dron.get_battery() )

def handler(signum, frame):
    print("[ABORT] Landing the Tello")
    dron.land()
    exit_event.set() # para que mate los threads
    exit()


def main():
    threads = [Thread( target=init_Controller, args=()),
               Thread( target=init_camera, args=()),
               Thread( target=init_sensor, args=())]

    for thread in threads:
        thread.start()
        thread.join()
    
    signal.signal(2, handler)

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